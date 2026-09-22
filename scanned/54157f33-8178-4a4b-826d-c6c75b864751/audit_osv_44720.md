# [C] Aim 3.29.1 Remote Code Execution via Unauthenticated Method Dispatch

## Summary
Severity: Critical
Advisory: CVE-2026-85663
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85663
Type: osv

## Details
Aim 3.29.1 remote tracking server fails to authenticate requests and dispatches arbitrary methods through getattr without allowlist validation. Unauthenticated attackers can register clients, instantiate Repo resources, and invoke arbitrary methods to read experiments or delete runs.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85663.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85663
- https://www.vulncheck.com/advisories/aim-3.29.1-remote-code-execution-via-unauthenticated-method-dispatch
- https://github.com/aimhubio/aim/issues/3412
- https://github.com/aimhubio/aim
- https://github.com/aimhubio/aim/blob/v3.29.1/aim/ext/transport/server.py
- https://github.com/aimhubio/aim/blob/v3.29.1/aim/ext/transport/tracking.py
