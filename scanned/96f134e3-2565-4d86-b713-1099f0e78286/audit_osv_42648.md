# [C] kotaemon 0.12.0 Unauthenticated Remote Code Execution via Insecure Deserialization

## Summary
Severity: Critical
Advisory: CVE-2026-69098
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-69098
Type: osv

## Details
kotaemon through 0.12.0 contains an insecure deserialization vulnerability in the check_connection endpoint that allows unauthenticated attackers to instantiate arbitrary Python classes by supplying crafted YAML/JSON input with a __type__ field. Attackers can exploit this to override the __type__ field with subprocess.check_output and arbitrary arguments, achieving remote code execution with application process privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69098.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-69098
- https://www.vulncheck.com/advisories/kotaemon-unauthenticated-remote-code-execution-via-insecure-deserialization
- https://github.com/Cinnamon/kotaemon
- https://github.com/Cinnamon/kotaemon/issues/844
