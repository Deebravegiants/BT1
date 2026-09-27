# [M] Bruno through 4.1.0 Arbitrary File Read via Unconfined Body File Path

## Summary
Severity: Medium
Advisory: CVE-2026-85665
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85665
Type: osv

## Details
Bruno versions through 4.1.0 fail to validate file paths in request body declarations, allowing attackers to read arbitrary local files by using parent-directory traversal segments. When a collection is executed, attackers can craft a request with a body:file path containing ../ sequences that resolve outside the collection directory, causing the application to read and exfiltrate arbitrary files to attacker-controlled endpoints.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85665.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85665
- https://www.vulncheck.com/advisories/bruno-3.4.2-arbitrary-file-read-via-unconfined-body-file-path
- https://github.com/usebruno/bruno/issues/8230
- https://github.com/usebruno/bruno
- https://github.com/usebruno/bruno/blob/v4.1.0/packages/bruno-cli/src/runner/prepare-request.js
