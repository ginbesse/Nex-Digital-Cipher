from __future__ import annotations

import argparse
import json
import textwrap
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path


DEVICE_LABELS = {
    "1": "website",
    "2": "airplane",
    "3": "car",
    "4": "ship",
    "5": "phone",
    "6": "computer",
    "7": "digital_app",
}


def slugify(value: str) -> str:
    value = value.lower().strip()
    chars = []
    for ch in value:
        if ch.isalnum():
            chars.append(ch)
        else:
            chars.append("-")
    slug = "".join(chars).strip("-")
    return slug or "generated-device"


def write_file(target: Path, content: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def fetch_dns_info(domain: str) -> dict | None:
    endpoint = f"https://dns.google/resolve?name={urllib.parse.quote(domain)}"
    try:
        with urllib.request.urlopen(endpoint, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    answers = payload.get("Answer", [])
    records = []
    for item in answers[:8]:
        records.append({
            "type": item.get("type"),
            "data": item.get("data"),
            "ttl": item.get("TTL"),
        })
    return {
        "status": payload.get("Status"),
        "records": records,
    }


def fetch_public_ip() -> dict:
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return {"ip": "unknown"}


def fetch_aircraft_snapshot() -> dict:
    try:
        with urllib.request.urlopen("https://opensky-network.org/api/states/all", timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return {"status": "unavailable", "flight_count": 0, "sample_flight": None}

    states = payload.get("states", []) or []
    sample = states[0] if states else []
    sample_flight = None
    if sample:
        sample_flight = {
            "icao24": sample[0],
            "callsign": sample[1],
            "origin_country": sample[2],
            "time_position": sample[3],
            "last_contact": sample[4],
            "longitude": sample[5],
            "latitude": sample[6],
            "baro_altitude": sample[7],
            "on_ground": sample[8],
            "velocity": sample[9],
            "true_track": sample[10],
            "vertical_rate": sample[11],
            "sensors": sample[12],
            "geo_altitude": sample[13],
            "squawk": sample[14],
            "spi": sample[15],
            "position_source": sample[16],
        }

    return {
        "status": "ok",
        "flight_count": len(states),
        "sample_flight": sample_flight,
    }


def build_website_code(
    domain: str,
    url: str,
    user_count: int,
    dns_info: dict | None = None,
    public_ip: dict | None = None,
) -> dict[str, str]:
    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{domain} | Smart Deployment</title>
  <link rel=\"stylesheet\" href=\"styles.css\" />
</head>
<body>
  <header class=\"hero\">
    <div class=\"hero-inner\">
      <p class=\"eyebrow\">Target domain: {domain}</p>
      <h1>{domain}</h1>
      <p class=\"subtitle\">This generated site is configured for {user_count} users.</p>
      <a class=\"cta\" href=\"{url}\">Open URL</a>
    </div>
  </header>

  <main class=\"grid\">
    <section class=\"card\">
      <h2>Traffic Profile</h2>
      <p>Expected user volume: {user_count}</p>
    </section>
    <section class=\"card\">
      <h2>Deployment Target</h2>
      <p>URL: {url}</p>
    </section>
  </main>

  <script src=\"script.js\"></script>
</body>
</html>
"""

    css = """body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: #0b1020;
  color: #f6f7fb;
}

.hero {
  padding: 4rem 1rem;
  background: linear-gradient(135deg, #1e3a8a, #2563eb);
}

.hero-inner {
  max-width: 900px;
  margin: 0 auto;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.8rem;
}

.cta {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #fff;
  color: #0b1020;
  text-decoration: none;
  border-radius: 999px;
  font-weight: bold;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.card {
  background: #111827;
  border-radius: 12px;
  padding: 1rem;
}
"""

    dns_json = json.dumps(dns_info or {"status": "unavailable", "records": []}, indent=2)
    public_ip_json = json.dumps(public_ip or {"ip": "unknown"}, indent=2)
    js = f"""const expectedUsers = {user_count};
const domain = \"{domain}\";
const url = \"{url}\";
const dnsInfo = {dns_json};
const publicIp = {public_ip_json};

console.log(\"Deploy target: \" + domain);
console.log(\"Expected users: \" + expectedUsers);
console.log(\"Primary URL: \" + url);
console.log(\"DNS metadata loaded: \" + dnsInfo.status);
console.log(\"Public IP: \" + publicIp.ip);
"""

    site_manifest = json.dumps({
        "domain": domain,
        "url": url,
        "expected_users": user_count,
        "dns_info": dns_info or {"status": "unavailable", "records": []},
        "public_ip": public_ip or {"ip": "unknown"},
    }, indent=2)

    return {
        "index.html": html,
        "styles.css": css,
        "script.js": js,
        "site_manifest.json": site_manifest,
    }


def build_airplane_code(
    device_name: str,
    user_count: int,
    aircraft_snapshot: dict | None = None,
) -> dict[str, str]:
    snapshot = aircraft_snapshot or {"status": "unavailable", "flight_count": 0, "sample_flight": None}
    flight_count = snapshot.get("flight_count", 0)
    sample_flight = snapshot.get("sample_flight") or {}
    longitude = sample_flight.get("longitude") or 0.0
    latitude = sample_flight.get("latitude") or 0.0
    callsign = sample_flight.get("callsign") or "UNKNOWN"

    code = textwrap.dedent(f"""\
    #include <stdio.h>
    #include <stdint.h>

    typedef struct {{
        uint16_t altitude_m;
        uint16_t speed_kmh;
        uint8_t passenger_count;
        int stable;
        int live_flight_count;
        double longitude;
        double latitude;
        const char *sample_callsign;
    }} FlightConfig;

    int main(void) {{
        FlightConfig cfg = {{
            .altitude_m = 12000,
            .speed_kmh = 850,
            .passenger_count = {user_count},
            .stable = 1,
            .live_flight_count = {flight_count},
            .longitude = {longitude},
            .latitude = {latitude},
            .sample_callsign = "{callsign}"
        }};

        printf("Aircraft module: {device_name}\\n");
        printf("Passengers: %u\\n", cfg.passenger_count);
        printf("Altitude: %u m\\n", cfg.altitude_m);
        printf("Speed: %u km/h\\n", cfg.speed_kmh);
        printf("Flight status: %s\\n", cfg.stable ? "stable" : "unstable");
        printf("OpenSky live flight snapshot count: %d\\n", cfg.live_flight_count);
        printf("Sample flight callsign: %s\\n", cfg.sample_callsign);
        printf("Sample coordinates: %.4f, %.4f\\n", cfg.longitude, cfg.latitude);
        return 0;
    }}
    """)
    manifest = json.dumps({
        "aircraft_snapshot": snapshot,
        "device_name": device_name,
        "user_count": user_count,
    }, indent=2)
    return {
        "flight_controller.c": code,
        "aircraft_snapshot.json": manifest,
    }


def build_car_code(device_name: str, user_count: int) -> dict[str, str]:
    code = textwrap.dedent(f"""\
    #include <stdio.h>

    int main(void) {{
        int passengers = {user_count};
        printf("Vehicle control module: {device_name}\\n");
        printf("Passenger capacity configured for: %d\\n", passengers);
        printf("Drive system ready.\\n");
        return 0;
    }}
    """)
    return {"vehicle_controller.c": code}


def build_ship_code(device_name: str, user_count: int) -> dict[str, str]:
    code = textwrap.dedent(f"""\
    #include <stdio.h>

    int main(void) {{
        int crew_count = {user_count};
        printf("Marine navigation controller: {device_name}\\n");
        printf("Crew count: %d\\n", crew_count);
        printf("Route engine ready.\\n");
        return 0;
    }}
    """)
    return {"marine_controller.c": code}


def build_phone_code(device_name: str, user_count: int) -> dict[str, str]:
    package = f"com.example.{slugify(device_name)}"
    code = textwrap.dedent(f"""\
    package {package}

    import androidx.appcompat.app.AppCompatActivity
    import android.os.Bundle

    class MainActivity : AppCompatActivity() {{
        override fun onCreate(savedInstanceState: Bundle?) {{
            super.onCreate(savedInstanceState)
            setContentView(R.layout.activity_main)
            println("Phone app initialized for {device_name}")
            println("Target active users: {user_count}")
        }}
    }}
    """)
    layout = textwrap.dedent(f"""\
    <?xml version="1.0" encoding="utf-8"?>
    <LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:orientation="vertical"
        android:padding="24dp">

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="{device_name}" />

        <TextView
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:text="Active users: {user_count}" />
    </LinearLayout>
    """)
    manifest = textwrap.dedent(f"""\
    <?xml version="1.0" encoding="utf-8"?>
    <manifest xmlns:android="http://schemas.android.com/apk/res/android">
        <application android:label="{device_name}" android:theme="@style/Theme.AppCompat.Light" />
    </manifest>
    """)
    gradle = textwrap.dedent(f"""\
    plugins {{
        id("com.android.application") version "8.5.0" apply false
        id("org.jetbrains.kotlin.android") version "1.9.24" apply false
    }}
    """)
    app_gradle = textwrap.dedent(f"""\
    plugins {{
        id("com.android.application")
        id("org.jetbrains.kotlin.android")
    }}

    android {{
        namespace = "{package}"
        compileSdk = 34

        defaultConfig {{
            applicationId = "{package}"
            minSdk = 24
            targetSdk = 34
            versionCode = 1
            versionName = "1.0"
        }}
    }}

    dependencies {{
        implementation("androidx.core:core-ktx:1.13.1")
        implementation("androidx.appcompat:appcompat:1.7.0")
        implementation("com.google.android.material:material:1.12.0")
    }}
    """)
    return {
        "settings.gradle.kts": gradle,
        "build.gradle.kts": app_gradle,
        "app/src/main/java/" + package.replace(".", "/") + "/MainActivity.kt": code,
        "app/src/main/res/layout/activity_main.xml": layout,
        "app/src/main/AndroidManifest.xml": manifest,
    }


def build_computer_code(device_name: str, user_count: int) -> dict[str, str]:
    code = textwrap.dedent(f"""\
    import json

    class ComputerRuntime:
        def __init__(self, device_name: str, user_count: int):
            self.device_name = device_name
            self.user_count = user_count

        def summary(self) -> str:
            return json.dumps({{
                "device": self.device_name,
                "user_count": self.user_count,
                "status": "ready"
            }})

    if __name__ == "__main__":
        runtime = ComputerRuntime("{device_name}", {user_count})
        print(runtime.summary())
    """)
    readme = textwrap.dedent(f"""\
    # {device_name} Desktop Runtime

    Run with:
    python3 main.py
    """)
    return {
        "main.py": code,
        "README.md": readme,
    }


def build_digital_app_code(device_name: str, user_count: int) -> dict[str, str]:
    app_code = textwrap.dedent(f"""\
    from flask import Flask, render_template

    app = Flask(__name__)

    @app.route("/")
    def home():
        return render_template("index.html", app_name="{device_name}", active_users={user_count})

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
    """)
    template = textwrap.dedent(f"""\
    <!doctype html>
    <html>
      <head>
        <title>{{ app_name }}</title>
        <style>
          body {{ font-family: Arial; padding: 2rem; }}
        </style>
      </head>
      <body>
        <h1>{{ app_name }}</h1>
        <p>Active users: {{ active_users }}</p>
      </body>
    </html>
    """)
    requirements = "Flask>=3.0\n"
    return {
        "app.py": app_code,
        "templates/index.html": template,
        "requirements.txt": requirements,
    }


def create_generation_output(
    device_type: str,
    user_count: int,
    input_value: str,
    domain: str | None = None,
    url: str | None = None,
) -> Path:
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{device_type}_{slugify(input_value)}_{now}"
    output_dir = Path("generated") / folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    if device_type == "website":
        dns_info = fetch_dns_info(domain or input_value)
        public_ip = fetch_public_ip()
        files = build_website_code(
            domain or input_value,
            url or "https://example.com",
            user_count,
            dns_info,
            public_ip,
        )
    elif device_type == "airplane":
        aircraft_snapshot = fetch_aircraft_snapshot()
        files = build_airplane_code(input_value, user_count, aircraft_snapshot)
    elif device_type == "car":
        files = build_car_code(input_value, user_count)
    elif device_type == "ship":
        files = build_ship_code(input_value, user_count)
    elif device_type == "phone":
        files = build_phone_code(input_value, user_count)
    elif device_type == "computer":
        files = build_computer_code(input_value, user_count)
    elif device_type == "digital_app":
        files = build_digital_app_code(input_value, user_count)
    else:
        raise ValueError("Unsupported device type")

    for filename, content in files.items():
        write_file(output_dir / filename, content)

    readme = textwrap.dedent(f"""\
    # Generated project

    Device type: {device_type}
    Input name: {input_value}
    Domain: {domain or '-'}
    URL: {url or '-'}
    User count: {user_count}

    Files created in: {output_dir}
    """)
    write_file(output_dir / "README.txt", readme)
    return output_dir


def prompt_for_selection() -> tuple[str, int, str, str, str]:
    print("\nChoose device type:")
    print("1) Website")
    print("2) Airplane")
    print("3) Car")
    print("4) Ship")
    print("5) Phone")
    print("6) Computer")
    print("7) Digital App")

    choice = input("Enter option number: ").strip()
    if choice not in DEVICE_LABELS:
        raise ValueError("Invalid option")

    device_type = DEVICE_LABELS[choice]
    user_count_raw = input("How many users should this system support? ").strip() or "1"
    try:
        user_count = int(user_count_raw)
    except ValueError as exc:
        raise ValueError("User count must be numeric") from exc

    if user_count < 1:
        raise ValueError("User count must be at least 1")

    if device_type == "website":
        domain = input("Domain name (example: example.com): ").strip() or "example.com"
        url = input("URL (example: https://example.com): ").strip() or "https://example.com"
        identifier = domain
    else:
        identifier = input("Device or app name: ").strip() or device_type
        url = ""
        domain = ""

    return device_type, user_count, identifier, domain, url


def demo_run() -> None:
    sample = create_generation_output(
        device_type="website",
        user_count=2500,
        input_value="example.com",
        domain="example.com",
        url="https://example.com",
    )
    print(f"Demo generated at: {sample}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Smart device code generator")
    parser.add_argument("--demo", action="store_true", help="Generate a demo website project")
    args = parser.parse_args()

    if args.demo:
        demo_run()
        return

    device_type, user_count, identifier, domain, url = prompt_for_selection()
    output_dir = create_generation_output(
        device_type=device_type,
        user_count=user_count,
        input_value=identifier,
        domain=domain,
        url=url,
    )
    print(f"\nGenerated files in: {output_dir}")
    print("You can now open the created source files and adapt them for your real deployment.")


if __name__ == "__main__":
    main()
