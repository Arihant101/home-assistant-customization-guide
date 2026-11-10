# The Home Assistant Glow-Up Guide 🫧

**Make your Home Assistant look amazing and do more, using only free and open-source tools.** Written for Home Assistant **2026.11**, running as **Container on Docker Desktop (Windows 11)** behind Tailscale. Everything here was checked in November 2026, and every GitHub link was confirmed to exist.

> **How to read this:** every section opens with a 🎯 **TL;DR**. ⚡ marks a quick win (under 10 minutes), 🧪 marks an advanced project, and 💸 marks something paid, with a free alternative listed next to it.

---

## 00 · TL;DR: the 60-minute glow-up

🎯 **TL;DR:** follow these 8 steps in order. Each one makes a visible difference.

1. ⚡ **Make a backup first.** Go to Settings → System → Backups → *Backup now*, then copy the file off the server. Syncthing works well for this (see §02).
2. ⚡ **Open the Marketplace** (Settings → Marketplace). HACS is now built in, so there's nothing to install manually (§01).
3. ⚡ **Install 4 basics:** Mushroom, Bubble Card, card-mod (or UIX), and Frosted Glass Themes (§04).
4. ⚡ **Turn on themes:** add `frontend: themes: !include_dir_merge_named themes` to `configuration.yaml`, then restart.
5. **Build one new dashboard:** use the *Sections* view with Mushroom chips at the top and Bubble Card pop-ups for each room (§06).
6. ⚡ **Connect your homelab:** Uptime Kuma, Jellyfin, Immich, Seerr, ntfy and Ollama all have **official** integrations now (§05).
7. **Add one automation that feels like magic:** if the homelab goes down, the lights flash red and your phone gets an ntfy alert (§11).
8. 🧪 **Pick a "signature" project:** a pixel clock (AWTRIX NG), a 3D floorplan, or a fully local voice assistant built on your Ollama (§12–§15).

---

## 01 · What changed in 2026 (old guides are now wrong)

🎯 **TL;DR:** HACS is now the built-in **Marketplace**, add-ons are now called **Apps**, and the old Core and Supervised install methods are no longer supported. Ignore YouTube tutorials that tell you to `wget get.hacs.xyz`.

| Release | What changed | Why you care |
|---|---|---|
| **2026.11** (Nov 4) | HACS became the built-in **Marketplace** under Settings → Marketplace. It works on every install type, Container included, with no manual downloads. | Existing HACS installs migrate automatically. The HACS installer stops at 2026.11. |
| 2026.11 | Installing from the Marketplace **no longer needs a restart** (updates still do). Updates show up under Settings → Updates. | Experimenting with cards is much faster now. |
| 2026.11 | Entities are now named from their **device + area** context. Renaming a device renames its entities, and entity IDs stay the same. | Some dashboard labels may look different after the update. Fix them by setting a card name. |
| 2026.11 | Copy, cut and paste **sections**. Auto-sections, Date/Alert/Sensor card options, hue sliders on light tiles, and automation **exclusions**. | Building dashboards takes fewer clicks. |
| 2026.6 | Weather forecast features on the tile card. | You may not need a custom weather card. |
| 2026.4 | **Native infrared** control and BLE e-paper (OpenDisplay). | Control your TV and AC with an IR blaster. |
| **2026.2** | **Add-ons were renamed to Apps.** Quick search opens with **Ctrl+K**. The new **Home dashboard** is the default Overview. | Apps need Home Assistant OS. On Container you run them as extra containers instead (§02). |
| 2025.12 | Support ended for the **Core and Supervised** install methods. Only **OS** and **Container** remain. | Your Container setup is officially supported. 👍 |

> ⚠️ **Marketplace safety notice:** before you install anything, HA asks you to accept that community projects are *not tested, audited, or supported* by the Home Assistant project, and that they run *inside your system*. Treat every custom card or integration like code you're running as root on your network (§14).

---

## 02 · Your setup: HA Container on Docker Desktop

🎯 **TL;DR:** your setup is supported, but Docker Desktop runs containers inside a hidden VM. That means **automatic discovery (mDNS/multicast), Bluetooth and USB don't reach Home Assistant**. Add devices by IP address, use network-based radios instead of USB ones, and run the old "Apps" as extra containers.

### What works and what doesn't on Docker Desktop

| Feature | Status | Workaround |
|---|---|---|
| Cloud integrations (Ring, Tuya, Alexa Devices) | ✅ Works | — |
| Integrations you add by IP (Hue, TP-Link Kasa, LG/Samsung TVs, Android TV Remote, Jellyfin, Immich…) | ✅ Works | Add them manually with their IP address. |
| Google Cast discovery | ⚠️ Usually not found automatically | In the Cast integration's options, set **Known hosts** to your Chromecasts' IP addresses. |
| Zeroconf/mDNS auto-discovery in general | ❌ Mostly broken | Docker's host networking only works on Linux hosts. On Docker Desktop it's an opt-in feature (4.34+) that runs inside the VM, so it isn't true LAN host networking. |
| Govee *local* (LAN API uses multicast) | ⚠️ Expect trouble | Use Govee BLE through an ESPHome Bluetooth proxy (§15), or try the integration and see. |
| USB Zigbee/Thread dongles | ❌ No simple passthrough | Use a **network coordinator** (Ethernet/PoE Zigbee, for example SMLIGHT SLZB-06) that Zigbee2MQTT/ZHA reach over TCP. |
| Bluetooth | ❌ | Use **ESPHome Bluetooth proxies**: cheap ESP32 boards that relay BLE over Wi-Fi. |
| Matter / Thread | ❌ Needs real host networking and IPv6 | Use one of the "level up" options below. |
| Apps (formerly add-ons) | ❌ Only on HA OS | Run them as **sidecar containers** (see the compose file below). |

### Level up (optional): get real host networking

| Option | Effort | What you gain |
|---|---|---|
| **A. Stay on Docker Desktop** | None | Fine for cloud and IP-based devices. Skip Matter. |
| **B. Docker Engine inside a WSL2 distro with mirrored networking** | 🧪 Medium | Windows 11 22H2+ supports `networkingMode=mirrored` in `.wslconfig`, which mirrors the Windows network interfaces into Linux and supports multicast. Docker Desktop itself **doesn't use** mirrored mode, so you run plain Docker Engine inside Ubuntu-on-WSL instead. A community guide recommends this exact setup ("don't use Docker Desktop for HA"). Your `/config` folder moves over unchanged. |
| **C. Move HA to your Arduino UNO Q** | Medium | It runs Debian Linux with Docker, so `--network=host` really works, and a published tutorial runs HA Container on it. It also has 4 GB RAM and a built-in microcontroller you can control over MQTT. |
| **D. Buy a dedicated box** (HA Green, N100 mini PC) | 💸 Low | Full HA OS with Apps. |

```ini
# Option B: C:\Users\<you>\.wslconfig   (then run: wsl --shutdown)
[wsl2]
networkingMode=mirrored
```

### "Apps" → sidecar containers (add these to your compose file)

```yaml
# docker-compose.yml: add these next to your existing homeassistant service
services:
  mosquitto:            # MQTT broker (replaces the Mosquitto App)
    image: eclipse-mosquitto:2
    restart: unless-stopped
    ports: ["1883:1883"]
    volumes:
      - ./mosquitto/config:/mosquitto/config   # add mosquitto.conf with listener + password_file
      - ./mosquitto/data:/mosquitto/data

  zigbee2mqtt:          # Zigbee without USB: point it at a network coordinator
    image: ghcr.io/koenkk/zigbee2mqtt
    restart: unless-stopped
    ports: ["8080:8080"]
    volumes: ["./z2m:/app/data"]   # in configuration.yaml: serial.port: tcp://<coordinator-ip>:6638

  esphome:              # DIY firmware dashboard
    image: ghcr.io/esphome/esphome
    restart: unless-stopped
    ports: ["6052:6052"]
    environment: [ESPHOME_DASHBOARD_USE_PING=true]   # mDNS is broken on Docker Desktop, so check online status by ping
    volumes: ["./esphome:/config"]

  whisper:              # local speech-to-text (Wyoming)
    image: rhasspy/wyoming-whisper
    command: --model tiny-int8 --language en
    restart: unless-stopped
    volumes: ["./whisper:/data"]

  piper:                # local text-to-speech (Wyoming)
    image: rhasspy/wyoming-piper
    command: --voice en_US-lessac-medium
    restart: unless-stopped
    volumes: ["./piper:/data"]

  openwakeword:         # "Okay Nabu" style wake words
    image: rhasspy/wyoming-openwakeword
    restart: unless-stopped

  nodered:              # visual automations (optional)
    image: nodered/node-red
    restart: unless-stopped
    ports: ["1880:1880"]
    volumes: ["./nodered:/data"]
```

- **Adding Wyoming services:** go to Settings → Devices & services → *Wyoming Protocol*. Use host `whisper` (port 10300), `piper` (10200) or `openwakeword` (10400). Service names resolve because they're in the same compose project.
- **Replacing the File editor App:** open the bind-mounted `config` folder in VS Code on Windows.
- ⚡ **Backups:** the built-in backup works on Container. Point **Syncthing** (which you already run) at the `config/backups` folder so every backup is copied to another device automatically.

---

## 03 · Remote access & hardening

🎯 **TL;DR:** you already have the best free remote access: **Tailscale**. Don't port-forward 8123. Turn on MFA, give family members non-admin accounts, and **check which IP failed logins come from before you enable `ip_ban`** (on Docker Desktop it might be the Docker gateway, and then you'd ban everyone).

| Option | Price | FOSS? | Notes |
|---|---|---|---|
| **Tailscale** (you have it) | Free personal plan | Clients are open source, the coordination server isn't | The Companion app works over your tailnet. There's also an official **Tailscale integration** that shows device status. |
| **Headscale** | Free | ✅ | Self-hosted Tailscale control server, for full FOSS. |
| **WireGuard** | Free | ✅ | Plain VPN. Needs a forwarded UDP port. |
| **Cloudflare Tunnel** | Free | ❌ | Public HTTPS without opening ports. |
| **Homeway** | Free tier, $3.49/mo supporter tier | ❌ | Remote access, free Alexa/Google bridging and a cloud MCP server. |
| 💸 **Home Assistant Cloud (Nabu Casa)** | ~$6.50/mo or $65/yr | — | The easiest option, and the money **funds Home Assistant development**. Worth it if you want to support the project. |

### Hardening checklist ✅

- [ ] **MFA:** go to your Profile → Security → enable a TOTP authenticator (an app like 2FAS or Aegis works).
- [ ] **Separate accounts:** your admin account for you, and **non-admin** users for family (they can still use dashboards).
- [ ] **No port forwarding.** Reach HA only through Tailscale.
- [ ] **Reverse proxy (Nginx Proxy Manager)?** Add `trusted_proxies`, or HA will reject the proxied requests:

```yaml
# configuration.yaml
http:
  use_x_forwarded_for: true
  trusted_proxies:
    - 172.16.0.0/12      # Docker networks: narrow this to NPM's actual subnet
    - 127.0.0.1
  # Turn these on only AFTER checking that failed-login notifications show the real client IP
  # (on Docker Desktop they may all show the same gateway IP, and then you'd lock yourself out):
  # ip_ban_enabled: true
  # login_attempts_threshold: 5
```

- [ ] **Secrets:** keep passwords and tokens in `secrets.yaml`, and add it to `.gitignore` before you push your config to GitHub. Run **gitleaks** on the repo first.
- [ ] **Tokens:** each long-lived access token (Homepage, n8n, Matter Hub, ha-fusion) gets its **own** name, so you can revoke one without breaking the others.
- [ ] **Future IoT VLAN:** when the Ubiquiti gear arrives, put IoT devices on their own VLAN and allow only HA → IoT traffic.

---

## 04 · Marketplace starter pack

🎯 **TL;DR:** install these first. Everything else in this guide builds on them.

<!-- gallery -->
| Preview | Name | What it does | Get it |
|---|---|---|---|
| <img src="https://user-images.githubusercontent.com/5878303/152332130-760cf616-5c40-4825-a482-bb8f1f0f5251.png" width="280"> | **[Mushroom](https://github.com/piitaya/lovelace-mushroom)** | Clean, rounded cards and chips with a visual editor. The classic first upgrade. | Marketplace |
| <img src="https://raw.githubusercontent.com/Clooos/Bubble-Card/main/.github/bubble-card.gif" width="280"> | **[Bubble Card](https://github.com/Clooos/Bubble-Card)** | Pop-ups that slide up from the bottom, sliders and separators, so your dashboard feels like a native app. Huge on Reddit. | Marketplace |
| <img src="https://user-images.githubusercontent.com/1299821/109144175-23239680-7761-11eb-8c1c-1e33139aa582.png" width="280"> | **[card-mod](https://github.com/thomasloven/lovelace-card-mod)** | Apply CSS to any card. Needed for blur, glow and glass effects. | Marketplace |
| — | **[UIX (UI eXtension)](https://github.com/Lint-Free-Technology/uix)** | Built on card-mod's ideas, it styles (nearly) any frontend element and adds templating ("Forge") and event wiring ("Broker"). | Marketplace |
| <img src="https://raw.githubusercontent.com/custom-cards/button-card/HEAD/examples/all.gif" width="280"> | **[button-card](https://github.com/custom-cards/button-card)** | The most flexible card there is. Behind most "how did they make that?!" dashboards. | Marketplace |
| <img src="https://user-images.githubusercontent.com/1299821/111066590-11abef80-84c0-11eb-809b-2843fd8610d8.gif" width="280"> | **[layout-card](https://github.com/thomasloven/lovelace-layout-card)** | Grid and masonry layouts with breakpoints for tablet, phone and desktop. | Marketplace |
| <img src="https://user-images.githubusercontent.com/1299821/188604118-ed2ad79c-0286-4392-b7be-cbc9c3f2ffd8.png" width="280"> | **[browser_mod](https://github.com/thomasloven/hass-browser_mod)** | Treat each browser or tablet as a device: pop-ups, navigation and kiosk control. | Marketplace |
| — | **[auto-entities](https://github.com/thomasloven/lovelace-auto-entities)** | Cards that fill themselves from filters (for example, "every light that's on"). | Marketplace |
| — | **[Spook 👻](https://github.com/frenck/spook)** | Extra actions plus *repairs* that find broken entity references after you rename things. | Marketplace |
| <img src="https://user-images.githubusercontent.com/2219836/228949675-f9699624-8abc-466c-bb04-250ce0f495b8.png" width="280"> | **[Adaptive Lighting](https://github.com/basnijholt/adaptive-lighting)** | Lights change color temperature with the sun all day. Set it once and forget it. | Marketplace |
| <img src="https://raw.githubusercontent.com/bramstroker/homeassistant-powercalc/master/docs/source/img/preview.gif" width="280"> | **[Powercalc](https://github.com/bramstroker/homeassistant-powercalc)** | Estimates power use for devices that have no meter, so your energy dashboard works without smart plugs. | Marketplace |
| — | **[Watchman](https://github.com/dummylabs/thewatchman)** | Reports missing entities and actions in your YAML, like a linter for your config. | Marketplace |

---

## 05 · Connect your stuff

🎯 **TL;DR:** nearly everything you own has an **official** integration. Cloud ones work on Docker Desktop as they are, and local ones need an IP address.

### Your devices

| Device | Integration | Type | Docker Desktop note |
|---|---|---|---|
| Echo / Alexa | **Alexa Devices** (official since 2025.6): announcements, TTS, DND, sensors | Cloud | ✅ |
| Echo (advanced) | [Alexa Media Player](https://github.com/alandtse/alexa_media_player) (Marketplace) | Cloud | ✅ Only if you need features the official one lacks |
| Ring | **Ring** (official) + [ring-mqtt](https://github.com/tsightler/ring-mqtt) for extras | Cloud | ✅ Read the 2026.11 breaking-change notes for Ring |
| Chromecast / Google speakers | **Google Cast** + **Google Assistant SDK** (broadcasts) | Local / Cloud | ⚠️ Set *Known hosts* |
| Philips Hue | **Philips Hue** | Local push | ✅ Add the bridge by IP |
| Kasa / TP-Link | **TP-Link Smart Home** | Local | ✅ Add by IP |
| Govee | **Govee lights local** / **Govee Bluetooth** | Local | ⚠️ Multicast; BLE needs a proxy |
| Tuya | **Tuya** (official, cloud) or [tuya-local](https://github.com/make-all/tuya-local) / [LocalTuya](https://github.com/xZetsubou/hass-localtuya) | Cloud / Local | ✅ / ✅ by IP |
| Smart TV | **LG webOS**, **Samsung Smart TV**, **Android TV Remote** | Local | ✅ Add by IP |

### Your homelab, inside Home Assistant 🧪

| Service | Integration | Cool idea |
|---|---|---|
| Uptime Kuma | **Uptime Kuma** (official) | If a monitor goes down: lights flash red and an ntfy alert goes out (§11) |
| Jellyfin | **Jellyfin** (official) | "Movie mode": when playback starts, dim the lights and close the blinds |
| Immich | **Immich** (official) | Photo slideshow on a wall tablet, plus storage stats |
| Seerr | **Seerr** (official, formerly Overseerr) | Announce on the Echo when a requested movie is ready |
| Sonarr / Radarr / qBittorrent | official | Pause torrents automatically when you start gaming |
| Syncthing | official | Alert when a folder stops syncing |
| ntfy | **ntfy** (official) | Your main notification channel, no Google needed |
| Ollama | **Ollama** (official) | A local LLM brain for voice (§12) |
| Tailscale | **Tailscale** (official) | Alert when a device has been offline for 24 hours |
| n8n | n8n's Home Assistant node + HA webhooks | Complex workflows (RSS → TTS morning brief) |
| Claude / AI agents | **Model Context Protocol Server** (official) | Let an MCP client control the home entities you choose |
| Homepage | Homepage's Home Assistant widget | Show HA stats on your Homepage dashboard |

### Control HA *from* Alexa or Google for free (no Nabu Casa)

- **[Home-Assistant-Matter-Hub](https://github.com/RiDDiX/home-assistant-matter-hub)** (RiDDiX fork). Publishes HA entities as Matter devices to Alexa, Google Home or Apple Home, locally. The original t0bst4r project ended in **January 2026**, so use this maintained fork. Docker image: `ghcr.io/riddix/home-assistant-matter-hub`. ⚠️ Matter needs mDNS, so expect to need option B or C from §02.
- **Emulated Hue** (built in): pretends to be a Hue bridge for basic on/off control with Alexa.
- **Manual Alexa Smart Home skill:** free, but expect 1–2 hours of AWS console setup.

---

## 06 · Dashboards: from default to drop-dead

🎯 **TL;DR:** start with the built-in **Sections** view and **tile cards** (they've improved a lot). Add Mushroom and Bubble Card on top. When you're bored, try a whole *framework* or a standalone dashboard app.

### The 5-step recipe

1. **New dashboard:** Settings → Dashboards → *Add* → **Sections**.
2. **Header row:** Mushroom *chips* for weather, who's home, alarm state and server status.
3. **Room sections:** one per room, with up to 4 tile or Mushroom cards each (matt8707's rule of thumb is to keep groups even).
4. **Details go in pop-ups:** a Bubble Card pop-up per room keeps the main view clean.
5. **Theme + background:** Frosted Glass or the DIY *Aero Glass* theme (§08) over a sky gradient.

### Frameworks & dashboard apps

<!-- gallery -->
| Preview | Name | What it does | Get it |
|---|---|---|---|
| <img src="https://raw.githubusercontent.com/acosta290/fluvy/main/docs/images/readme/hero.webp" width="280"> | **[Fluvy](https://github.com/acosta290/fluvy)** | Redesigns all of HA: 52 styled cards, 5 automatic dashboards, 15 palettes. Needs HA 2026.9+. | Marketplace custom repo (Integration) |
| <img src="https://raw.githubusercontent.com/Krystosterone/dashhaus/HEAD/docs/src/assets/skins/phone-orb-light.webp" width="280"> | **[Dashhaus](https://github.com/Krystosterone/dashhaus)** | Two complete looks ("Orb" round and soft, "Field" hardware-panel style) with no YAML. First shown on Reddit. | Marketplace custom repo (Dashboard) |
| <img src="https://raw.githubusercontent.com/UI-Lovelace-Minimalist/UI/main/docs/assets/img/example_home.png" width="280"> | **[UI Lovelace Minimalist](https://github.com/UI-Lovelace-Minimalist/UI)** | The famous rounded minimalist card framework. | Marketplace |
| <img src="https://raw.githubusercontent.com/dwainscheeren/dwains-dashboard-next/HEAD/docs/media/dd-next-1.11-home-areas.jpg" width="280"> | **[Dwains Dashboard Next](https://github.com/dwainscheeren/dwains-dashboard-next)** | Builds dashboards automatically from your areas. (DD3 is being phased out, so use Next.) | Marketplace |
| <img src="https://raw.githubusercontent.com/TheRealSimon42/simon42-dashboard-strategy/main/assets/Screenshot-simon42-strategy.png" width="280"> | **[simon42 Dashboard Strategy](https://github.com/TheRealSimon42/simon42-dashboard-strategy)** | A dashboard *strategy* that creates itself from your rooms. | Marketplace |
| <img src="https://raw.githubusercontent.com/knowald/ha-fusion/HEAD/static/preview.png" width="280"> | **[ha-fusion](https://github.com/knowald/ha-fusion)** | A separate SvelteKit app with drag-and-drop editing and slide-to-dim. This is the maintained fork of matt8707's original. | Docker container |
| <img src="https://raw.githubusercontent.com/oyvhov/tunet/HEAD/public/Main.png" width="280"> | **[Tunet](https://github.com/oyvhov/tunet)** | React dashboard with a drag-and-drop grid and energy views. `docker compose up -d`. | Docker container |
| — | **[Homie Dashboard](https://github.com/Big-Edge2297/homie-dashboard)** | Touch-first wall-tablet app with full-screen music, calendar, camera and solar modes. ⚠️ Stores a token in plain text, so give it its own user. | Marketplace custom repo |
| <img src="https://raw.githubusercontent.com/willsanderson/Hemma/HEAD/docs/images/hero-light.webp" width="280"> | **[Hemma](https://github.com/willsanderson/Hemma)** | Mobile-first YAML dashboard inspired by Homio. | Manual YAML |

---

## 07 · The card gallery

🎯 **TL;DR:** browse, install from the Marketplace, and add with the card picker. Use the search box at the top of the site to filter.

<!-- gallery -->
| Preview | Name | What it does | Get it |
|---|---|---|---|
| <img src="https://raw.githubusercontent.com/pkissling/clock-weather-card/HEAD/docs/previews/hero.gif" width="280"> | **[Clock Weather Card](https://github.com/pkissling/clock-weather-card)** | Big clock, animated weather icons and a forecast bar. Perfect for a wall tablet. | Marketplace |
| <img src="https://user-images.githubusercontent.com/457678/52977264-edf34980-33cc-11e9-903b-cee43b307ed8.png" width="280"> | **[mini-graph-card](https://github.com/kalkih/mini-graph-card)** | Small, smooth sensor graphs. | Marketplace |
| <img src="https://raw.githubusercontent.com/RomRider/apexcharts-card/master/docs/Header.png" width="280"> | **[ApexCharts Card](https://github.com/RomRider/apexcharts-card)** | Serious charts: multiple Y axes, data transforms, "now" markers. | Marketplace |
| <img src="https://raw.githubusercontent.com/dbuezas/lovelace-plotly-graph-card/HEAD/docs/resources/example1.png" width="280"> | **[Plotly Graph Card](https://github.com/dbuezas/lovelace-plotly-graph-card)** | Zoomable, pannable, interactive history. | Marketplace |
| <img src="https://user-images.githubusercontent.com/61006057/227771568-78497ecc-e863-46f2-b29e-e15c7c20a154.gif" width="280"> | **[Power Flow Card Plus](https://github.com/flixlix/power-flow-card-plus)** | Animated energy flow between grid, solar, battery and home. | Marketplace |
| <img src="https://raw.githubusercontent.com/MindFreeze/ha-sankey-chart/HEAD/img/example.png" width="280"> | **[Sankey Chart](https://github.com/MindFreeze/ha-sankey-chart)** | Where your watts go, room by room, as a sankey diagram. | Marketplace |
| <img src="https://user-images.githubusercontent.com/457678/47517460-9282d600-d888-11e8-9705-cf9ec3698c3c.png" width="280"> | **[Mini Media Player](https://github.com/kalkih/mini-media-player)** | Compact media controls with artwork backgrounds (great with Jellyfin). | Marketplace |
| <img src="https://raw.githubusercontent.com/Nerwyn/universal-remote-card/main/assets/screenshot.png" width="280"> | **[Universal Remote Card](https://github.com/Nerwyn/universal-remote-card)** | Build a TV remote with a touchpad, D-pad and app shortcuts. | Marketplace |
| <img src="https://raw.githubusercontent.com/rejuvenate/lovelace-horizon-card/main/images/full-dark.png" width="280"> | **[Horizon Card](https://github.com/rejuvenate/lovelace-horizon-card)** | Sun (and moon) arc across the sky with rise and set times. | Marketplace |
| <img src="https://raw.githubusercontent.com/nicufarmache/lovelace-big-slider-card/master/assets/preview-default-light.gif" width="280"> | **[Big Slider Card](https://github.com/nicufarmache/lovelace-big-slider-card)** | A whole-card brightness slider: swipe to dim. | Marketplace |
| <img src="https://raw.githubusercontent.com/totaldebug/atomic-calendar-revive/master/.github/img/atomic_calendar_revive.png" width="280"> | **[Atomic Calendar Revive](https://github.com/totaldebug/atomic-calendar-revive)** | A much nicer calendar card. | Marketplace |
| <img src="https://raw.githubusercontent.com/nielsfaber/scheduler-card/main/screenshots/Demonstration.gif" width="280"> | **[Scheduler Card](https://github.com/nielsfaber/scheduler-card)** + [component](https://github.com/nielsfaber/scheduler-component) | Schedules your family can edit, without writing automations. | Marketplace |
| <img src="https://raw.githubusercontent.com/NemesisRE/kiosk-mode/HEAD/example.png" width="280"> | **[Kiosk Mode](https://github.com/NemesisRE/kiosk-mode)** | Hides the header and sidebar for wall tablets. | Marketplace |
| <img src="https://raw.githubusercontent.com/joseluis9595/lovelace-navbar-card/HEAD/docs/content/img/navbar-card-hero-rounded.png" width="280"> | **[Navbar Card](https://github.com/joseluis9595/lovelace-navbar-card)** | App-style bottom navigation bar. | Marketplace |
| <img src="https://raw.githubusercontent.com/brunosabot/streamline-card/HEAD/images/hero.png" width="280"> | **[Streamline Card](https://github.com/brunosabot/streamline-card)** | Reusable card templates, so you stop copy-pasting YAML. | Marketplace |
| <img src="https://raw.githubusercontent.com/custom-cards/stack-in-card/HEAD/docs/Example.png" width="280"> | **[Stack In Card](https://github.com/custom-cards/stack-in-card)** | Merges several cards into one seamless card. | Marketplace |
| <img src="https://raw.githubusercontent.com/Nerwyn/custom-card-features/main/assets/example_tile.png" width="280"> | **[Custom Card Features](https://github.com/Nerwyn/custom-card-features)** | Adds custom buttons, sliders and selectors to the *native* tile card. | Marketplace |
| <img src="https://raw.githubusercontent.com/benct/lovelace-multiple-entity-row/master/example.png" width="280"> | **[Multiple Entity Row](https://github.com/benct/lovelace-multiple-entity-row)** | Several values on one entity row. | Marketplace |
| — | **[Swiss Army Knife Card](https://github.com/AmoebeLabs/swiss-army-knife-card)** | SVG-based gauges and widgets you design yourself. Very niche, very pretty. | Marketplace |
| <img src="https://user-images.githubusercontent.com/3549445/293683009-196cd771-7d29-4975-a741-0a5c8a76e095.png" width="280"> | **[ha-floorplan](https://github.com/ExperienceLovelace/ha-floorplan)** | Interactive SVG floorplans (rooms light up when lights are on). | Marketplace |
| <img src="https://raw.githubusercontent.com/PiotrMachowski/lovelace-xiaomi-vacuum-map-card/master/docs/media/tiles.png" width="280"> | **[Xiaomi Vacuum Map Card](https://github.com/PiotrMachowski/lovelace-xiaomi-vacuum-map-card)** | Live vacuum map with zone cleaning (works with many brands). | Marketplace |
| <img src="https://raw.githubusercontent.com/dermotduffy/advanced-camera-card/main/docs/images/advanced-camera-card.png" width="280"> | **[Advanced Camera Card](https://github.com/dermotduffy/advanced-camera-card)** | Camera views with a timeline, clips and PTZ (formerly the Frigate card). | Marketplace |

---

## 08 · Themes (and a DIY Frutiger Aero theme)

🎯 **TL;DR:** **Frosted Glass** is the closest ready-made match to a Frutiger Aero look. For the full glossy-sky-and-grass vibe, paste the **Aero Glass** theme below.

**Setup once:** add this to `configuration.yaml`, create `/config/themes`, then restart:

```yaml
frontend:
  themes: !include_dir_merge_named themes
```

Pick a theme under **Profile → Theme** and set the mode to *Auto* for themes with light and dark variants.

<!-- gallery -->
| Preview | Name | Look | Get it |
|---|---|---|---|
| — | **[Frosted Glass](https://github.com/wessamlauf/homeassistant-frosted-glass-themes)** | Transparent, blurred cards over a background image. Light, dark and "Lite" (no blur, for old tablets). Needs card-mod or UIX. | Marketplace |
| — | **[Simple Dreams](https://github.com/dizzydnallov/simple_dreams)** | A layered landscape illustration with glass cards at the top. Tablet-first. | Manual |
| <img src="https://raw.githubusercontent.com/catppuccin/home-assistant/HEAD/assets/preview.webp" width="280"> | **[Catppuccin](https://github.com/catppuccin/home-assistant)** | Pastel palettes (Latte, Frappé, Macchiato, Mocha) that even style the code editors. | Marketplace |
| <img src="https://raw.githubusercontent.com/basnijholt/lovelace-ios-themes/media/screenshots/overview.gif" width="280"> | **[iOS Themes](https://github.com/basnijholt/lovelace-ios-themes)** | Apple Home look, 28 variants with wallpapers. | Marketplace |
| <img src="https://raw.githubusercontent.com/TilmanGriesel/graphite/HEAD/docs/public/assets/screenshot/dark.png" width="280"> | **[Graphite](https://github.com/TilmanGriesel/graphite)** | Calm and minimal, with **E-Ink** variants for e-paper screens. | Marketplace |
| <img src="https://raw.githubusercontent.com/aFFekopp/noctis/master/docs/screenshots/pc/1.jpg" width="280"> | **[Noctis](https://github.com/aFFekopp/noctis)** | The classic dark-blue theme. | Marketplace |
| <img src="https://raw.githubusercontent.com/Nerwyn/material-you-utilities/main/assets/headline.png" width="280"> | **[Material You](https://github.com/Nerwyn/material-you-utilities)** | Material Design 3 Expressive, with colors generated from a seed color. Matches your Android phone. | Marketplace |
| <img src="https://user-images.githubusercontent.com/38670315/210792537-f25c740d-1ad3-4ac7-8a31-59ad04cf38fb.png" width="280"> | **[HA-LCARS](https://github.com/th3jesta/ha-lcars)** | Star Trek LCARS. Your house becomes a starship. 🖖 | Marketplace |
| <img src="https://raw.githubusercontent.com/flejz/hass-cyberpunk-2077-theme/master/docs/theme-overview.png" width="280"> | **[Cyberpunk 2077](https://github.com/flejz/hass-cyberpunk-2077-theme)** | Neon HUD look. Load the Rajdhani font to complete it. | Marketplace |
| <img src="https://i.imgur.com/DHbESc9.png" width="280"> | **[Synthwave](https://github.com/bbbenji/synthwave-hass)** | Neon pink and purple, '80s retro. | Marketplace |
| <img src="https://raw.githubusercontent.com/awolkers/home-assistant-themes/master/docs/dark_turqoise.png" width="280"> | **[Dark Theme Pack](https://github.com/awolkers/home-assistant-themes)** | Modern dark themes in 6 accent colors. | Marketplace |
| <img src="https://raw.githubusercontent.com/VonWelter/neumorphism/HEAD/themes.jpg" width="280"> | **[Neumorphism](https://github.com/VonWelter/neumorphism)** | Soft, raised "neumorphic" UI, mobile-first. | Manual |
| <img src="https://raw.githubusercontent.com/JuanMTech/google_dark_theme/master/images/Google%20Dark%20Mode%201.jpg" width="280"> | **[Google Dark](https://github.com/JuanMTech/google_dark_theme)** | Google Home app vibes. | Marketplace |
| — | **[Gruvbox](https://github.com/kizza/homeassistant-gruvbox-theme)** | Warm, earthy retro palette with matching Mushroom colors. | Marketplace |
| — | **[MNML](https://github.com/bfmatei/ha-mnml)** | Minimal card set and theme; color only where it needs attention. | Marketplace custom repo |
| <img src="https://user-images.githubusercontent.com/5878303/152695688-9d705231-500c-49e7-82f5-69e206da95db.png" width="280"> | **[Mushroom Themes](https://github.com/piitaya/lovelace-mushroom-themes)** | Themes tuned for Mushroom (try "Mushroom Shadow"). | Marketplace |

### 🫧 DIY: the "Aero Glass" theme (Frutiger Aero vibes)

Glossy sky-blue glass, aqua highlights and a grass-green accent, with **no background image needed** (the sky-to-grass gradient is pure CSS). It requires **card-mod** (for the blur). Save as `/config/themes/aero_glass.yaml`, then run the action `frontend.reload_themes`.

```yaml
Aero Glass:
  card-mod-theme: Aero Glass
  modes:
    light:
      primary-color: "#0a84ff"
      accent-color: "#34c759"
      primary-text-color: "#05314f"
      secondary-text-color: "#2c6a8c"
      lovelace-background: >-
        radial-gradient(ellipse at 20% 0%, rgba(255,255,255,.9) 0%, transparent 45%),
        linear-gradient(180deg, #3fb6f2 0%, #9fdcf7 42%, #d9f5ff 62%, #8fdc78 82%, #3fae4a 100%)
      ha-card-background: "linear-gradient(180deg, rgba(255,255,255,.78) 0%, rgba(255,255,255,.42) 52%, rgba(225,246,255,.55) 100%)"
      ha-card-border-radius: "22px"
      ha-card-border-color: "rgba(255,255,255,.9)"
      ha-card-box-shadow: "0 10px 28px rgba(0,70,130,.20), inset 0 1px 0 rgba(255,255,255,.95)"
      app-header-background-color: "rgba(10,120,215,.55)"
      app-header-text-color: "#ffffff"
      sidebar-background-color: "rgba(255,255,255,.55)"
      state-icon-color: "#0a84ff"
    dark:
      primary-color: "#4cc2ff"
      accent-color: "#5be37d"
      primary-text-color: "#e8f7ff"
      secondary-text-color: "#9fd3ef"
      lovelace-background: >-
        radial-gradient(ellipse at 70% 0%, rgba(76,194,255,.35) 0%, transparent 50%),
        linear-gradient(180deg, #021a33 0%, #063a63 55%, #0b4d3a 100%)
      ha-card-background: "linear-gradient(180deg, rgba(255,255,255,.16) 0%, rgba(255,255,255,.06) 100%)"
      ha-card-border-radius: "22px"
      ha-card-border-color: "rgba(160,220,255,.35)"
      ha-card-box-shadow: "0 10px 28px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.25)"
      app-header-background-color: "rgba(2,26,51,.6)"
      sidebar-background-color: "rgba(2,26,51,.55)"
  card-mod-card: |
    ha-card {
      backdrop-filter: blur(14px) saturate(160%);
      -webkit-backdrop-filter: blur(14px) saturate(160%);
    }
```

> 💡 For extra gloss, add a soft white "shine" stripe across the top of each card with `ha-card::before` in `card-mod-card`, then pair the theme with a **Bubble Card** pop-up per room.

---

## 09 · Hall of fame: dashboards from Reddit & GitHub

🎯 **TL;DR:** these are the setups people keep copying. Steal ideas freely, and give credit if you share your result.

<!-- gallery -->
| Preview | Name | Why it's famous | Source |
|---|---|---|---|
| <img src="https://user-images.githubusercontent.com/4341881/173772319-907d6821-b96c-4d07-96d0-c0fd02efe2b6.png" width="280"> | **[Madelena's "hass-config-public"](https://github.com/Madelena/hass-config-public)** | The isometric wireframe-floorplan look that inspired a generation of Reddit dashboards. | GitHub |
| <img src="https://raw.githubusercontent.com/matt8707/hass-config/master/www/img/dash.png" width="280"> | **[matt8707/hass-config](https://github.com/matt8707/hass-config)** | Iconic wall-tablet design built with button-card and layout-card. No longer maintained, but still a goldmine to learn from. | GitHub |
| — | **[Homio: "The wife approved the dashboard"](https://github.com/iamtherufus/Homio)** | A calm, room-render wall tablet layout that also works on phones. Started as a Reddit post. | GitHub + Reddit |
| <img src="https://raw.githubusercontent.com/jlnbln/My-HA-Dashboard/main/images/home_desktop.png" width="280"> | **[Rounded-Bubble (jlnbln)](https://github.com/jlnbln/My-HA-Dashboard)** | Bubble Card rooms, a per-user layout and a custom Music Assistant player. | GitHub |
| <img src="https://raw.githubusercontent.com/clooos/Home-Assistant-Mobile-First/master/www/images/Home%20Assistant%20-%20UI%20V4%20-%20Main%20dashboard.jpg" width="280"> | **[Mobile-First (Clooos)](https://github.com/Clooos/Home-Assistant-Mobile-First)** | The phone-app-style dashboard that led to Bubble Card. (Archived, so use Bubble Card today.) | GitHub |
| — | **[Flux UI](https://github.com/ElementZoom/Flux-UI-Home-Assistant-Dashboard)** | Material 3 look: room cards change color with temperature, live radar. Started on [Reddit](https://www.reddit.com/r/homeassistant/comments/1um2c41/comment/p6r2v9p/?context=3). | GitHub + Reddit |
| <img src="https://raw.githubusercontent.com/ruudmens/home-assistant-dashboard/HEAD/images/home-dashboard.png" width="280"> | **[LazyAdmin wall display](https://github.com/ruudmens/home-assistant-dashboard)** | Square tiles with a header image that changes between day and night. Entity IDs are placeholders, so you can fork it. | GitHub |
| <img src="https://raw.githubusercontent.com/Petro31/home-assistant-config/master/www/images/github_images/overview.png" width="280"> | **[Petro31](https://github.com/Petro31/home-assistant-config)** | From one of the top template experts on the HA forum. Amazing remote cards. | GitHub |
| <img src="https://raw.githubusercontent.com/jazzyisj/home-assistant-config/master/www/screenshots/browser_home.png" width="280"> | **[jazzyisj](https://github.com/jazzyisj/home-assistant-config)** | A huge, well-documented config with a clean browser UI. | GitHub |
| <img src="https://raw.githubusercontent.com/ugomeda/home-assistant-epaper-remote/HEAD/preview.jpg" width="280"> | **[E-ink remote](https://github.com/ugomeda/home-assistant-epaper-remote)** | A *physical* handheld remote with an e-paper screen. [Reddit post](https://www.reddit.com/r/homeassistant/comments/1qs0q11/eink_remote_for_home_assistant/). | GitHub + Reddit |
| — | **[Pokémon-style floorplan](https://www.reddit.com/r/homeassistant/comments/1hrkku1/pokemon_style_floorplan/)** | A home redrawn as a classic Pokémon map, with day and night versions. Built with `picture-elements`. | Reddit |
| — | **[Illustrated animated floorplan](https://www.reddit.com/r/homeassistant/comments/1w65sse/illustrated_floorplan_dashboard_with_animation/)** | A commissioned hand-drawn floorplan with day/night animations, running on a wall TV. | Reddit |
| — | **[Lit floor map (ha-floorplan)](https://www.reddit.com/r/homeassistant/comments/1tdaqrh/floor_map_is_amazing/)** | Dark and lit renders, and each light glows according to its brightness. | Reddit |
| — | **[Live 3D floorplan that "got out of hand"](https://www.reddit.com/r/homeassistant/comments/1wzc637/my_floorplan_dashboard_got_out_of_hand_live/)** | Blender scene with live weather, real lamp colors, TV Ambilight and an animated cat. | Reddit |
| — | **[AI-built energy page](https://www.reddit.com/r/homeassistant/comments/1wt5qii/claude_opus_is_a_game_changer/)** | A self-contained HTML/JS page served from `/local/`, written with an AI coding agent. | Reddit |
| — | **[Wall tablet dashboard (932 upvotes)](https://www.reddit.com/r/homeassistant/comments/1glcfmu/my_workinprogress_simple_wall_tablet_dashboard/)** | A simple, beautiful wall-tablet layout. Read the comments for the YAML. | Reddit |
| — | **[Graphite theme launch](https://www.reddit.com/r/homeassistant/comments/1hpmrsm/graphite_theme/)** | Where the Graphite theme was first shown. | Reddit |
| <img src="https://raw.githubusercontent.com/Burningstone91/smart-home-setup/master/git-pictures/smart_home_diagram.png" width="280"> | **[Burningstone91/smart-home-setup](https://github.com/Burningstone91/smart-home-setup)** | Documented like an infrastructure project, with network and system diagrams. Great reading for a cyber student. | GitHub |

> 🔎 **Find more:** on [r/homeassistant](https://www.reddit.com/r/homeassistant/), sort by **Top → All time** and filter by the *Personal Setup* flair. People usually post their YAML in the comments when asked.

---

## 10 · GitHub configs worth studying

🎯 **TL;DR:** read real configs to learn structure (packages, blueprints, secrets). Don't copy them whole.

| Repo | Known for |
|---|---|
| [frenck/home-assistant-config](https://github.com/frenck/home-assistant-config) | Config of HA's lead developer. Very clean structure. |
| [CCOSTAN/Home-AssistantConfig](https://github.com/CCOSTAN/Home-AssistantConfig) | "Bear Stone" smart home, one of the longest-running public configs. |
| [basnijholt/home-assistant-config](https://github.com/basnijholt/home-assistant-config) | From the author of Adaptive Lighting and iOS Themes. |
| [Petro31/home-assistant-config](https://github.com/Petro31/home-assistant-config) | Template wizardry. |
| [thejeffreystone/home-assistant-configuration](https://github.com/thejeffreystone/home-assistant-configuration) | Announcement and TTS automations with personality. |
| [geekofweek/homeassistant](https://github.com/geekofweek/homeassistant) | Huge, well-organized automation library. |
| [arsaboo/homeassistant-config](https://github.com/arsaboo/homeassistant-config) | Long-running config with many integrations. |
| [skalavala/mysmarthome](https://github.com/skalavala/mysmarthome) | Jinja and template recipes. |
| [frenck/awesome-home-assistant](https://github.com/frenck/awesome-home-assistant) | ⭐ The master "awesome list." |
| [EPMatt/awesome-ha-blueprints](https://github.com/EPMatt/awesome-ha-blueprints) | Ready-made blueprints for remotes and buttons. |

---

## 11 · Automations that feel like magic

🎯 **TL;DR:** build these in the visual editor. The YAML below uses the 2024.10+ syntax (`triggers:` / `actions:`).

| Idea | Uses | Difficulty |
|---|---|---|
| 🔴 Homelab down → lights pulse red + ntfy alert | Uptime Kuma, Govee/Hue, ntfy | ⚡ |
| 🎬 Jellyfin starts playing → dim the lights, pause Echo music | Jellyfin, Alexa Devices | ⚡ |
| 🚪 Ring doorbell → camera snapshot to your phone + "someone's at the door" on every Echo | Ring, ntfy, Alexa Devices | ⚡ |
| 🌅 Sunrise alarm → lights fade up over 15 minutes | Adaptive Lighting / light transitions | ⚡ |
| 🧺 Washing machine done (power drops) → announce it | Kasa plug with power monitoring | ⚡ |
| 🎮 PC gaming → pause qBittorrent | qBittorrent, HASS.Agent / System Monitor | 🧪 |
| 🏠 Room-level presence → lights follow you | Bermuda BLE + ESP32 proxies (§15) | 🧪 |
| 📰 Morning brief → weather + calendar + RSS read out on the Echo | n8n / Assist + TTS | 🧪 |

```yaml
# Homelab down → red pulse + push notification
alias: "🔴 Homelab monitor down"
triggers:
  - trigger: state
    entity_id: binary_sensor.jellyfin_status     # any Uptime Kuma monitor entity
    to: "off"
    for: "00:02:00"
actions:
  - action: light.turn_on
    target: { entity_id: light.desk_lamp }
    data: { color_name: red, flash: long }
  - action: notify.send_message
    target: { entity_id: notify.ntfy_homelab }   # your ntfy notify entity
    data:
      title: "Homelab alert"
      message: "{{ state_attr(trigger.entity_id, 'friendly_name') }} has been down for 2 minutes"
mode: single
```

> 🧩 **Blueprints** turn this into one click: Settings → Automations → Blueprints → *Import*, then browse [awesome-ha-blueprints](https://github.com/EPMatt/awesome-ha-blueprints).

---

## 12 · Voice & local AI (your Ollama finally gets a job)

🎯 **TL;DR:** **Whisper** (speech-to-text) → **Ollama** (thinking) → **Piper** (speech) is a free voice assistant that runs entirely on your hardware. On Container, Whisper, Piper and openWakeWord run as the sidecar containers from §02.

1. Add the **Wyoming Protocol** integration for whisper, piper and openwakeword (§02).
2. Add the **Ollama** integration and point it at your Ollama server (a tool-capable model is needed to control devices).
3. Settings → Voice assistants → *Add* → conversation agent **Ollama**, STT **faster-whisper**, TTS **piper**.
4. Talk to it from the Companion app, or 💸 buy a **Home Assistant Voice Preview Edition** (~$69, physical mic mute switch), or DIY an ESP32 satellite.
5. 🧪 Expose only a short list of entities to the LLM. The docs suggest staying **under ~25** for Ollama.

| Extra | What it does |
|---|---|
| **[LLM Vision](https://github.com/valentinfrlch/ha-llmvision)** | AI descriptions of camera snapshots ("a delivery driver left a box") |
| **Model Context Protocol Server** (official) | Lets MCP clients (Claude Desktop and others) control the entities you choose |
| **[home-llm](https://github.com/acon96/home-llm)** | Small local models fine-tuned specifically for home control |
| **[Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation)** | Function calling for any OpenAI-compatible API (Ollama exposes one) |

---

## 13 · Cameras & NVR

🎯 **TL;DR:** **Frigate** is the free answer to cloud camera subscriptions: local recording plus AI object detection.

<!-- gallery -->
| Preview | Name | What it does | Get it |
|---|---|---|---|
| <img src="https://raw.githubusercontent.com/blakeblackshear/frigate-hass-integration/master/images/lovelace-card.png" width="280"> | **[Frigate](https://github.com/blakeblackshear/frigate)** + [integration](https://github.com/blakeblackshear/frigate-hass-integration) | Local NVR with person and car detection. Send events to HA, then snapshot → ntfy. | Docker + Marketplace |
| <img src="https://raw.githubusercontent.com/AlexxIT/go2rtc/HEAD/website/images/webui-net.png" width="280"> | **[go2rtc](https://github.com/AlexxIT/go2rtc)** | Universal camera restreamer (RTSP → WebRTC) for instant live view. | Docker |
| — | **[WebRTC Camera](https://github.com/AlexxIT/WebRTC)** | Near-zero-latency camera card. | Marketplace |
| — | **Matter cameras** (2026.11) | Matter 1.5 cameras with WebRTC live video. Two-way audio is a Labs preview and needs HTTPS. | Built in |

---

## 14 · 🛡️ Cyber corner

🎯 **TL;DR:** treat HA as an attack surface and as a security monitoring tool.

### War story: one HACS bug = admin access

HACS versions **before 1.10.0** had a **path traversal** bug in the `/hacsfiles/` endpoint. It let **unauthenticated** attackers read `.storage/auth`, which holds credentials and refresh tokens, and then forge valid tokens for **admin access** (CVSS 7.5, catalogued as CVE-2021-47942). It was fixed in 2021, but it shows why you should **keep everything updated and never expose HA directly to the internet**. Another 2026 advisory showed how a malicious **entity name** from an integration could trigger XSS in the Statistics Graph card.

### Build a security dashboard

| Integration | What it shows |
|---|---|
| **Pi-hole** / **AdGuard Home** | Blocked queries, toggle blocking |
| **Nmap Tracker** | Which devices are on your LAN. Alert on **new unknown devices** 🚨 |
| **UniFi Network** (when the UDM arrives) | Clients, firewall events, presence |
| **Uptime Kuma** | Service health |
| **Glances** / **System monitor** | CPU, RAM and disk for your server |
| **Certificate Expiry** | Alerts before your HTTPS certificates expire |
| **Speedtest.net** | ISP performance history |

```yaml
# Alert on every failed HA login (then check which IP it shows; see §03)
alias: "🚨 Failed login attempt"
triggers:
  - trigger: persistent_notification
    update_type: added
    notification_id: http-login
actions:
  - action: notify.send_message
    target: { entity_id: notify.ntfy_homelab }
    data:
      title: "HA login failed"
      message: "{{ trigger.notification.message }}"
```

### Hacker-aesthetic ideas 🕶️

- **LCARS** or **Cyberpunk 2077** theme on a spare tablet → a "SOC wall" view of your network.
- Graph Pi-hole queries over time with ApexCharts, like a mini SIEM.
- Store your config in a **private** Git repo, run **gitleaks** in a pre-commit hook, and enable branch protection.
- Use Wireshark on a mirrored port to see which IoT devices phone home, then block them with Pi-hole.

---

## 15 · DIY, niche & weird hardware 🧪

🎯 **TL;DR:** ESP32 boards ($5–10) plus **ESPHome** let you build almost anything. These are the coolest projects.

<!-- gallery -->
| Preview | Name | What it does | Get it |
|---|---|---|---|
| <img src="https://raw.githubusercontent.com/smarthomejunkie/Ulanzi-Awtrix-BluePrints/HEAD/images/ulanzi-tc001.jpg" width="280"> | **Ulanzi TC001 + [AWTRIX NG](https://github.com/Blueforcer/awtrix3)** | A ~$50 pixel clock that shows notifications, homelab stats and weather over MQTT. AWTRIX 3 has ended, and its repo now points to the **AWTRIX NG** rewrite. Matching [blueprints](https://github.com/smarthomejunkie/Ulanzi-Awtrix-BluePrints). | Flash in the browser |
| — | **[ESPHome](https://github.com/esphome/esphome)** | YAML → firmware for ESP32 sensors, displays and LED controllers. Runs in your compose stack. | Docker |
| <img src="https://raw.githubusercontent.com/agittins/bermuda/HEAD/img/screenshots/person-tracker.png" width="280"> | **[Bermuda BLE Trilateration](https://github.com/agittins/bermuda)** | Room-level presence from your phone or watch using ESPHome Bluetooth proxies. This also **fixes Docker Desktop's lack of Bluetooth**. | Marketplace |
| — | **[ESPresense](https://github.com/ESPresense/ESPresense)** | An alternative room-presence firmware for ESP32 (MQTT). | Flash |
| <img src="https://raw.githubusercontent.com/klaasnicolaas/home-assistant-glow/HEAD/docs/static/img/home-assistant-glow.jpg" width="280"> | **[Home Assistant Glow](https://github.com/klaasnicolaas/home-assistant-glow)** | Read your electric meter's pulse LED → live energy data. | ESPHome |
| — | **[openHASP](https://github.com/HASwitchPlate/openHASP)** | Turns cheap ESP32 touchscreens into custom wall panels. | Flash |
| <img src="https://raw.githubusercontent.com/Hypfer/valetudo/master/docs/pages/general/img/operation_principle.png" width="280"> | **[Valetudo](https://github.com/Hypfer/Valetudo)** | Cloud-free firmware for supported robot vacuums. Fully local, with a [map card](https://github.com/Hypfer/lovelace-valetudo-map-card). | Root + flash |
| <img src="https://raw.githubusercontent.com/sibbl/hass-lovelace-kindle-screensaver/main/assets/sample.png" width="280"> | **[Kindle dashboard](https://github.com/sibbl/hass-lovelace-kindle-screensaver)** | An old Kindle becomes an e-ink HA display (pair it with the Graphite E-Ink theme). | Docker |
| <img src="https://raw.githubusercontent.com/Koenkk/zigbee2mqtt/HEAD/images/architecture-new.png" width="280"> | **[Zigbee2MQTT](https://github.com/Koenkk/zigbee2mqtt)** | Run Zigbee without vendor hubs. Pair it with a **network** coordinator on Docker Desktop. | Docker |
| — | **Arduino UNO Q ↔ HA via MQTT** | Your UNO Q's Linux side runs HA or a Python bridge, and its STM32 microcontroller drives pins or relays. A published tutorial toggles the onboard LED from an HA dashboard. | DIY |
| — | **Native IR** (2026.4) + **LoRaWAN** (2026.11) | Control IR devices, and long-range low-power sensors through ChirpStack or The Things Network. | Built in |
| — | **Zigbee Green Power** (2026.11) | Batteryless kinetic switches (like Friends of Hue) in ZHA. | Built in |

---

## 16 · Wall panels & kiosks

🎯 **TL;DR:** an old Android tablet + the HA Companion app + **Kiosk Mode** is the free wall panel. 💸 Fully Kiosk Browser's PLUS license is paid, and **WallPanel** is the FOSS alternative.

| Option | Cost | Notes |
|---|---|---|
| Old tablet + Companion app + [Kiosk Mode](https://github.com/NemesisRE/kiosk-mode) | Free | Easiest. Use [browser_mod](https://github.com/thomasloven/hass-browser_mod) to control it remotely. |
| [WallPanel](https://github.com/WallPanel-Project/wallpanel-android) | Free, FOSS | Android kiosk app with camera motion wake and MQTT. |
| Raspberry Pi + Chromium `--kiosk` | Cheap | A dedicated screen that boots straight into a dashboard. |
| Kindle e-ink | Free | §15. |
| openHASP ESP32 touchscreen | ~$20–40 | Fully custom, no tablet needed. |

---

## 17 · 💸 Paid → free swaps

| Paid thing | Free / FOSS alternative |
|---|---|
| Nabu Casa remote access | Tailscale (you have it), Headscale, WireGuard |
| Nabu Casa Alexa/Google link | Home-Assistant-Matter-Hub (RiDDiX), Emulated Hue, manual skill |
| Cloud voice (Alexa/Google) | Whisper + Ollama + Piper (§12) |
| Fully Kiosk PLUS | WallPanel, Companion app + Kiosk Mode |
| LaMetric Time | Ulanzi TC001 + AWTRIX NG |
| Ring Protect / Nest Aware | Frigate + local cameras |
| Hue Bridge / vendor hubs | Zigbee2MQTT or ZHA + a coordinator |
| Robot-vacuum cloud | Valetudo |
| IFTTT Pro | HA automations, Node-RED, n8n |

---

## 18 · Keep learning

- **[r/homeassistant](https://www.reddit.com/r/homeassistant/):** dashboards, help, inspiration.
- **[Home Assistant Community forum](https://community.home-assistant.io/):** the "Share your projects" and themes categories.
- **[LazyAdmin](https://lazyadmin.nl/tag/home-assistant/)**, **[SmartHomeScene](https://smarthomescene.com/)**, **[Smart Home Junkie](https://www.smarthomejunkie.net/)**, **[simon42](https://www.simon42.com/)** (German): up-to-date guides and release breakdowns.
- **[Home Assistant release notes](https://www.home-assistant.io/blog/categories/release-notes/):** read them before every update, especially the *Backward-incompatible changes* section.

---

## Sources

- [Home Assistant 2026.11 release notes (Marketplace, naming, Matter cameras)](https://www.home-assistant.io/blog/2026/11/04/release-202611/)
- [Home Assistant 2026.2 release notes (Apps rename, Quick search, Home dashboard)](https://www.home-assistant.io/blog/2026/02/04/release-20262/)
- [Deprecating Core & Supervised installs (2025)](https://home-assistant.io/blog/2025/05/22/deprecating-core-and-supervised-installation-methods-and-32-bit-systems/)
- [Docker host network driver docs (Docker Desktop 4.34+)](https://docs.docker.com/engine/network/drivers/host/)
- [Docker forum: Docker Desktop doesn't use WSL mirrored mode](https://forums.docker.com/t/host-networking-not-working-on-docker-desktop-in-wsl2-with-mirrored-mode/147994)
- [Microsoft: WSL mirrored mode networking](https://learn.microsoft.com/en-us/windows/wsl/networking)
- [HA Community: Mini PC + Windows + WSL2 + Docker](https://community.home-assistant.io/t/mini-pc-windows-wsl2-docker-homeassistant/769603)
- [Run Home Assistant on the Arduino UNO Q (Hackster)](https://www.hackster.io/tech_nickk/run-home-assistant-on-the-arduino-uno-q-docker-mqtt-setup-8a3b0a)
- [Alexa Devices integration docs](https://www.home-assistant.io/integrations/alexa_devices)
- [Home-Assistant-Matter-Hub (RiDDiX fork) docs](https://riddix.github.io/home-assistant-matter-hub/)
- [LazyAdmin: Best Home Assistant themes 2026](https://lazyadmin.nl/smart-home/best-home-assistant-themes/)
- [LazyAdmin: 14 dashboard examples](https://lazyadmin.nl/smart-home/home-assistant-dashboard-examples/)
- [CNX Software: Connect ZBT-2](https://www.cnx-software.com/2025/11/20/home-assistant-connect-zbt-2-zigbee-thread-usb-adapter/)
- [HACS path traversal advisory (CVE-2021-47942)](https://feed.craftedsignal.io/briefs/2026-05-hacs-path-traversal/)
- [Homeway pricing comparison](https://neilturner.me.uk/2025/02/23/)
- [Home Assistant Cloud pricing (2026)](https://subger.com/en/service/home-assistant-cloud)

*Made with 🫧 for a Frutiger Aero-loving cyber student. Free and open source only; paid things are marked 💸.*
