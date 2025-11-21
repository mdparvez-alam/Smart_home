import time
import flet as ft


# --------- Simple data model ----------

class Device:
    def __init__(self, id, name, type_, is_on=False, slider_value=None):
        self.id = id
        self.name = name
        self.type = type_          # "light", "door", "thermostat", "fan"
        self.is_on = is_on         # for on/off devices
        self.slider_value = slider_value  # for slider devices


def main(page: ft.Page):
    page.title = "Smart Home Controller + Simulator"
    page.padding = 20
    page.bgcolor = ft.colors.GREY_100
    page.horizontal_alignment = ft.CrossAxisAlignment.START
    page.vertical_alignment = ft.MainAxisAlignment.START

    # ---- devices ----
    light = Device("light1", "Living Room Light", "light", is_on=False)
    door = Device("door1", "Front Door", "door", is_on=True)  # True = locked
    thermostat = Device("thermo1", "Thermostat", "thermostat", slider_value=22)
    fan = Device("fan1", "Ceiling Fan", "fan", slider_value=0)

    devices = {d.id: d for d in [light, door, thermostat, fan]}

    # ---- action log storage (for statistics + details) ----
    action_log = []  # list of dicts: {time, device, action, user}

    # ---- statistics controls (we fill them when building statistics view) ----
    power_text = ft.Text("", size=16)
    log_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time")),
            ft.DataColumn(ft.Text("Device")),
            ft.DataColumn(ft.Text("Action")),
            ft.DataColumn(ft.Text("User")),
        ],
        rows=[],
    )

    # ---------- helper functions ----------

    def current_power_watts() -> int:
        """Very simple 'simulated' power consumption."""
        power = 0
        if light.is_on:
            power += 10
        # door doesn't consume power in this simple model
        if thermostat.slider_value is not None:
            # base 80W + 5W per degree above 20
            power += 80 + max(0, thermostat.slider_value - 20) * 5
        if fan.slider_value is not None:
            power += fan.slider_value * 30  # 0..90 W
        return power

    def update_power_text():
        power_text.value = f"Current simulated power: {current_power_watts()} W"
        power_text.update()

    def log_action(device: Device, action: str, user: str = "User"):
        t = time.strftime("%H:%M:%S")
        action_log.append(
            {"time": t, "device": device.id, "action": action, "user": user}
        )

        # keep last 50 rows only
        if len(action_log) > 50:
            del action_log[0 : len(action_log) - 50]

        # update table UI
        log_table.rows.clear()
        for entry in reversed(action_log):  # latest first
            log_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(entry["time"])),
                        ft.DataCell(ft.Text(entry["device"])),
                        ft.DataCell(ft.Text(entry["action"])),
                        ft.DataCell(ft.Text(entry["user"])),
                    ]
                )
            )
        log_table.update()

    # ---------- views ----------

    def build_overview_view() -> ft.View:

        # ---- Living Room Light card ----
        light_status = ft.Text(
            f"Status: {'ON' if light.is_on else 'OFF'}", size=14
        )

        def toggle_light(e):
            light.is_on = not light.is_on
            action = "Turn ON" if light.is_on else "Turn OFF"
            light_status.value = f"Status: {'ON' if light.is_on else 'OFF'}"
            light_button.text = "Turn OFF" if light.is_on else "Turn ON"
            light_status.update()
            light_button.update()
            log_action(light, action)
            update_power_text()

        light_button = ft.ElevatedButton(
            "Turn ON" if not light.is_on else "Turn OFF", on_click=toggle_light
        )

        light_card = ft.Card(
            content=ft.Container(
                padding=20,
                width=280,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.LIGHTBULB_OUTLINE),
                                ft.Text(
                                    "Living Room Light",
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                ),
                            ]
                        ),
                        light_status,
                        ft.Text("Tap to switch the light."),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton(
                                    "Details",
                                    on_click=lambda e: page.go(
                                        f"/device/{light.id}"
                                    ),
                                ),
                                light_button,
                            ],
                        ),
                    ],
                ),
            )
        )

        # ---- Front Door card ----
        door_status = ft.Text(
            f"Door: {'LOCKED' if door.is_on else 'UNLOCKED'}", size=14
        )

        def toggle_door(e):
            door.is_on = not door.is_on
            action = "Lock" if door.is_on else "Unlock"
            door_status.value = (
                f"Door: {'LOCKED' if door.is_on else 'UNLOCKED'}"
            )
            door_button.text = "Unlock" if door.is_on else "Lock"
            door_status.update()
            door_button.update()
            log_action(door, action)
            update_power_text()

        door_button = ft.ElevatedButton(
            "Unlock" if door.is_on else "Lock", on_click=toggle_door
        )

        door_card = ft.Card(
            content=ft.Container(
                padding=20,
                width=280,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.DOOR_FRONT),
                                ft.Text(
                                    "Front Door",
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                ),
                            ]
                        ),
                        door_status,
                        ft.Text("Tap to lock / unlock the door."),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton(
                                    "Details",
                                    on_click=lambda e: page.go(
                                        f"/device/{door.id}"
                                    ),
                                ),
                                door_button,
                            ],
                        ),
                    ],
                ),
            )
        )

        # ---- Thermostat card ----
        thermo_value_text = ft.Text(
            f"Set point: {thermostat.slider_value:.1f} °C", size=14
        )

        def thermo_changed(e):
            thermostat.slider_value = e.control.value
            thermo_value_text.value = (
                f"Set point: {thermostat.slider_value:.1f} °C"
            )
            thermo_value_text.update()
            log_action(thermostat, f"Set to {thermostat.slider_value:.1f} °C")
            update_power_text()

        thermo_slider = ft.Slider(
            min=10,
            max=30,
            divisions=20,
            value=thermostat.slider_value,
            on_change_end=thermo_changed,
            width=220,
        )

        thermo_card = ft.Card(
            content=ft.Container(
                padding=20,
                width=280,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.DEVICE_THERMOSTAT),
                                ft.Text(
                                    "Thermostat",
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                ),
                            ]
                        ),
                        thermo_value_text,
                        ft.Text("Use slider to change temperature."),
                        thermo_slider,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.TextButton(
                                    "Details",
                                    on_click=lambda e: page.go(
                                        f"/device/{thermostat.id}"
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            )
        )

        # ---- Ceiling fan card ----
        fan_value_text = ft.Text(
            f"Fan speed: {int(fan.slider_value)}", size=14
        )

        def fan_changed(e):
            fan.slider_value = int(e.control.value)
            fan_value_text.value = f"Fan speed: {int(fan.slider_value)}"
            fan_value_text.update()
            log_action(fan, f"Set speed to {int(fan.slider_value)}")
            update_power_text()

        fan_slider = ft.Slider(
            min=0,
            max=3,
            divisions=3,
            value=fan.slider_value,
            on_change_end=fan_changed,
            width=220,
        )

        fan_card = ft.Card(
            content=ft.Container(
                padding=20,
                width=280,
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(ft.icons.AIR),
                                ft.Text(
                                    "Ceiling Fan",
                                    weight=ft.FontWeight.BOLD,
                                    size=16,
                                ),
                            ]
                        ),
                        fan_value_text,
                        ft.Text("0 = OFF, 3 = MAX."),
                        fan_slider,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.TextButton(
                                    "Details",
                                    on_click=lambda e: page.go(
                                        f"/device/{fan.id}"
                                    ),
                                )
                            ],
                        ),
                    ],
                ),
            )
        )

        # ---- final layout for overview ----
        return ft.View(
            "/",
            controls=[
                ft.Text(
                    "Smart Home Controller",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text("Overview", size=14, color=ft.colors.BLUE),
                ft.Divider(),
                ft.Text(
                    "On/Off devices",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(controls=[light_card, door_card]),
                ft.Divider(),
                ft.Text(
                    "Slider controlled devices",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(controls=[thermo_card, fan_card]),
            ],
        )

    def build_statistics_view() -> ft.View:
        update_power_text()
        chart_placeholder = ft.Container(
            height=260,
            border=ft.border.all(1, ft.colors.GREY_300),
            padding=10,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Power consumption (simulated)",
                        weight=ft.FontWeight.BOLD,
                        size=18,
                    ),
                    power_text,
                    ft.Text(
                        "(You can later replace this container with a real "
                        "line chart if you want.)",
                        size=12,
                        italic=True,
                    ),
                ]
            ),
        )

        return ft.View(
            "/statistics",
            controls=[
                ft.Text(
                    "Smart Home Controller",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text("Statistics", size=14, color=ft.colors.BLUE),
                ft.Divider(),
                chart_placeholder,
                ft.Divider(),
                ft.Text(
                    "Action log",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(
                    expand=True,
                    content=ft.ListView(
                        controls=[log_table], expand=True, spacing=10
                    ),
                ),
            ],
        )

    def build_device_details_view(device_id: str) -> ft.View:
        device = devices[device_id]

        # state string
        if device.type == "light":
            state_str = "ON" if device.is_on else "OFF"
        elif device.type == "door":
            state_str = "LOCKED" if device.is_on else "UNLOCKED"
        elif device.type == "thermostat":
            state_str = f"{device.slider_value:.1f} °C"
        elif device.type == "fan":
            state_str = str(int(device.slider_value))
        else:
            state_str = "-"

        # last few actions for this device
        recent = [a for a in reversed(action_log) if a["device"] == device.id][
            0:10
        ]
        recent_controls = []
        for a in recent:
            recent_controls.append(
                ft.Text(
                    f"{a['time']} - {a['action']} ({a['user']})",
                    size=14,
                )
            )
        if not recent_controls:
            recent_controls.append(ft.Text("No actions yet.", size=14))

        return ft.View(
            f"/device/{device.id}",
            controls=[
                ft.Text(
                    "Smart Home Controller",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Divider(),
                ft.Text(
                    f"{device.name} details",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(f"ID: {device.id}"),
                ft.Text(f"Type: {device.type}"),
                ft.Text(f"State: {state_str}"),
                ft.Divider(),
                ft.Text(
                    "Recent actions",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Column(controls=recent_controls, spacing=5),
                ft.ElevatedButton(
                    "Back to overview",
                    on_click=lambda e: page.go("/"),
                ),
            ],
        )

    # ---------- navigation callbacks ----------

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        if page.route == "/":
            page.views.append(build_overview_view())
        elif page.route == "/statistics":
            page.views.append(build_statistics_view())
        elif page.route.startswith("/device/"):
            device_id = page.route.split("/")[-1]
            if device_id in devices:
                page.views.append(build_device_details_view(device_id))
            else:
                page.views.append(build_overview_view())
        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        page.update()

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # add simple top-right navigation between Overview and Statistics
    page.appbar = ft.AppBar(
        title=ft.Text("Smart Home Controller + Simulator"),
        center_title=False,
        actions=[
            ft.TextButton("Overview", on_click=lambda e: page.go("/")),
            ft.TextButton(
                "Statistics", on_click=lambda e: page.go("/statistics")
            ),
        ],
    )

    page.go("/")  # start at overview


ft.app(target=main)
