# [C] Juggle 1.6.0 Unauthenticated RCE via Exposed H2 Console

## Summary
Severity: Critical
Advisory: CVE-2026-67208
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-67208
Type: osv

## Details
Juggle through 1.6.0 contains a remote code execution vulnerability that allows unauthenticated remote attackers to execute arbitrary OS commands by connecting to the exposed H2 database web console using default shipped credentials. Attackers can access the unprotected /h2-console endpoint, authenticate with default credentials, and leverage the H2 CREATE ALIAS Runtime.exec() technique to execute arbitrary commands, resulting in root-level code execution when running the stock Docker image.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67208
- https://www.vulncheck.com/advisories/juggle-unauthenticated-rce-via-exposed-h2-console
- https://github.com/somta/Juggle/issues/86
- https://github.com/somta/Juggle
