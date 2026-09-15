# [C] Arelle < 2.39.10 Unauthenticated RCE via /rest/configure

## Summary
Severity: Critical
Advisory: CVE-2026-42796
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-42796
Type: osv

## Details
Arelle before 2.39.10 contains an unauthenticated remote code execution vulnerability in the /rest/configure REST endpoint that accepts a plugins query parameter and forwards it to the plugin manager without authentication or authorization. Attackers can supply a URL to a malicious Python file through the plugins parameter, causing the Arelle webserver to download and execute the attacker-controlled code within the Arelle process with its privileges.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42796.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42796
- https://www.vulncheck.com/advisories/arelle-unauthenticated-rce-via-rest-configure
- https://github.com/Arelle/Arelle/pull/2320
- https://github.com/Arelle/Arelle/releases/tag/2.39.10
