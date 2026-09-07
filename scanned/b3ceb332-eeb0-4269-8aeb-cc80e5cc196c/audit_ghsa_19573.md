# [C] Dpanel's hard-coded JWT secret leads to remote code execution

## Summary
Severity: Critical
Advisory: GHSA-j752-cjcj-w847
CVE: CVE-2025-30206
CWE: CWE-321, CWE-453, CWE-547
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-04-15
Source: https://github.com/advisories/GHSA-j752-cjcj-w847
Type: github-advisory

## Affected
- Go: `github.com/donknap/dpanel` — affected >=0 <1.6.1

## Details
### Summary
The Dpanel service contains a hardcoded JWT secret in its default configuration, allowing attackers to generate valid JWT tokens and compromise the host machine.

### Details
The Dpanel service, when initiated using its default configuration, includes a hardcoded JWT secret embedded directly within its source code. This security flaw allows attackers to analyze the source code, discover the embedded secret, and craft legitimate JWT tokens. By forging these tokens, an attacker can successfully bypass authentication mechanisms, impersonate privileged users, and gain unauthorized administrative access. Consequently, this enables full control over the host machine, potentially leading to severe consequences such as sensitive data exposure, unauthorized command execution, privilege escalation, or further lateral movement within the network environment. It is recommended to replace the hardcoded secret with a securely generated value and load it from secure configuration storage to mitigate this vulnerability.


### PoC
The core code snippet is shown below:
```python
import jwt

def generate_jwt(appname):

    payload = {
        "SECRET_KEY"："SECRET_VALUE",
    }
    print("appname:", appname)
    print("payload:", str(payload))
    token = jwt.encode(payload, SECRET_KEY.format(APP_NAME=appname), algorithm="HS256")
    return token

appname = "SECRET_KEY"
token = generate_jwt(appname)
print("url token:", token)
```

### Impact
Attackers who successfully exploit this vulnerability can write arbitrary files to the host machine's file system, and all users with Dpanel versions less than 1.6.1 are affected.

## References
- https://github.com/donknap/dpanel/security/advisories/GHSA-j752-cjcj-w847
- https://nvd.nist.gov/vuln/detail/CVE-2025-30206
- https://github.com/donknap/dpanel
- https://pkg.go.dev/vuln/GO-2025-3612
