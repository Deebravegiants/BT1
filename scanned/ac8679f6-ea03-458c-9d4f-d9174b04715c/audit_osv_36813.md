# [H] Chartbrew: Remote Code Execution (RCE) via Vulnerable API

## Summary
Severity: High
Advisory: CVE-2026-25888
Aliases: GHSA-875w-45c2-gxq8
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-25888
Type: osv

## Details
Chartbrew is an open-source web application that can connect directly to databases and APIs and use the data to create charts. Prior to version 4.8.1, there is a remote code execution vulnerability via a vulnerable API. This issue has been patched in version 4.8.1.

## References
- https://github.com/chartbrew/chartbrew/releases/tag/v4.8.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25888.json
- https://github.com/chartbrew/chartbrew/security/advisories/GHSA-875w-45c2-gxq8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25888
