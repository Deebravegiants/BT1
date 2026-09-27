# [H] Lack of entropy allows registered low-privileged users of Litmus to crack valid JWT tokens and gain admin privileges

## Summary
Severity: High
Advisory: CVE-2025-14261
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-14261
Type: osv

## Details
The Litmus platform uses JWT for authentication and authorization, but the secret being used for signing the JWT is only 6 bytes long at its core, which makes it extremely easy to crack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14261.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-14261
- https://research.jfrog.com/vulnerabilities/litmus-jwt-missing-entropy-elevation-jfsa-2025-001648159/
- https://github.com/litmuschaos/litmus/pull/5324
