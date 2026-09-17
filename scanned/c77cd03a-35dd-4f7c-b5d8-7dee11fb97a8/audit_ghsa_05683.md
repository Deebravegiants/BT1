# [C] Unfurl's debug mode cannot be disabled due to string config parsing (Werkzeug debugger exposure)

## Summary
Severity: Critical
Advisory: GHSA-vg9h-jx4v-cwx2
CWE: CWE-489
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-29
Source: https://github.com/advisories/GHSA-vg9h-jx4v-cwx2
Type: github-advisory

## Affected
- PyPI: `dfir-unfurl` — affected >=0

## Details
### Summary
The Unfurl web app enables Flask debug mode even when configuration sets `debug = False`. The config value is read as a string and passed directly to `app.run(debug=...)`, so any non-empty string evaluates truthy. This leaves the Werkzeug debugger active by default.

### Details
- `unfurl/app.py:web_app()` reads `debug` via `config['UNFURL_APP'].get('debug')`, which returns a string.
- `UnfurlApp.__init__` passes that string directly to `app.run(debug=unfurl_debug, ...)`.
- If `unfurl.ini` omits `debug`, the default argument is the string `"True"`.
- As a result, debug mode is effectively always on and cannot be reliably disabled via config.

### PoC
1. Create a local `unfurl.ini` with `debug = False` under `[UNFURL_APP]`.
2. Run the server using `unfurl_app` (or `python -c 'from unfurl.app import web_app; web_app()'`).
3. Observe server logs showing `Debug mode: on` / `Debugger is active!`.
4. The included PoC script `security_poc/poc_debug_mode.py --spawn` automates this check.

### PoC Script (inline)
```python
#!/usr/bin/env python3
"""
Unfurl Debug Mode PoC (Corrected)
================================

This PoC demonstrates that Unfurl's Flask debug mode is effectively
**always enabled by default** due to string parsing of the `debug`
config value. Even `debug = False` in `unfurl.ini` evaluates truthy
when passed to `app.run(debug=...)`.

Two modes:
1) --spawn (default): launch a local Unfurl server with debug=False
   in a temp config and inspect logs for "Debug mode: on".
2) --target: attempt a remote indicator check (best-effort; may be silent
   if no exception is triggered).
"""

import argparse
import os
import subprocess
import sys
import tempfile
import textwrap
import time


def run_spawn_check() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    ini_contents = textwrap.dedent("""
    [UNFURL_APP]
    host = 127.0.0.1
    port = 5055
    debug = False
    remote_lookups = false

    [API_KEYS]
    bitly =
    macaddress_io =
    """).strip() + "\n"

    with tempfile.TemporaryDirectory() as tmp:
        ini_path = os.path.join(tmp, 'unfurl.ini')
        with open(ini_path, 'w') as f:
            f.write(ini_contents)

        env = os.environ.copy()
        env['PYTHONPATH'] = repo_root

        cmd = [sys.executable, '-c', 'from unfurl.app import web_app; web_app()']
        proc = subprocess.Popen(
            cmd,
            cwd=tmp,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Allow server to start and emit logs
        time.sleep(2)
        proc.terminate()
        try:
            out, err = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()

        output = (out or "") + (err or "")

    print("\n[+] Debug mode spawn check")
    print("    Config: debug = False")

    if "Debug mode: on" in output or "Debugger is active" in output:
        print("    ✅ Debug mode is ON despite debug=False (vulnerable)")
    else:
        print("    ⚠️  Debug mode not detected in logs (check output below)")

    if output.strip():
        print("\n--- server output (truncated) ---")
        print("\n".join(output.splitlines()[:15]))
        print("--- end ---")


def run_remote_probe(target: str) -> None:
    import requests

    print("\n[+] Remote debug indicator probe (best-effort)")
    print(f"    Target: {target}")

    # This app does not easily throw exceptions from user input, so
    # absence of indicators does NOT prove debug is off.
    probe_urls = [
        f"{target.rstrip('/')}/__nonexistent__",
    ]

    detected = False
    for url in probe_urls:
        try:
            resp = requests.get(url, timeout=10)
            if "Werkzeug Debugger" in resp.text or "Traceback" in resp.text:
                detected = True
                print("    ✅ Debug indicators found")
                break
        except Exception as e:
            print(f"    ⚠️  Probe failed: {e}")

    if not detected:
        print("    ⚠️  No debug indicators found (this is not definitive)")


def main():
    parser = argparse.ArgumentParser(description='Unfurl debug mode PoC (corrected)')
    parser.add_argument('--spawn', action='store_true', help='Run local spawn check (default)')
    parser.add_argument('--target', help='Target Unfurl URL for remote probe')
    args = parser.parse_args()

    if args.target:
        run_remote_probe(args.target)
    else:
        run_spawn_check()


if __name__ == '__main__':
    main()
```

### Impact
If the service is exposed beyond localhost (bound to 0.0.0.0 or reverse-proxied), an attacker can access the Werkzeug debugger. This can disclose sensitive information and may allow remote code execution if a debugger PIN is obtained. At minimum, stack traces and environment details are exposed on errors.

## References
- https://github.com/obsidianforensics/unfurl/security/advisories/GHSA-vg9h-jx4v-cwx2
- https://github.com/obsidianforensics/unfurl/commit/4c0a07ab1e9af3a1ddf0e7f47153ec9ba77946dd
- https://github.com/obsidianforensics/unfurl
