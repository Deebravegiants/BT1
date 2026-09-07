# [H] extract-zip unvalidated symlink path traversal

## Summary
Severity: High
Advisory: GHSA-jmr9-qjv8-65gv
CVE: CVE-2026-56876
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-jmr9-qjv8-65gv
Type: github-advisory

## Affected
- npm: `extract-zip` — affected >=0

## Details
extract-zip does not validate symlink targets when extracting zip archives. When processing a malicious zip file containing a symlink with a relative path like '../../../../etc/passwd', extract-zip will extract the symlink without validation, allowing it to point outside the extraction directory. Depending on how extract-zip is used, an attacker could read or write to arbitrary files.

## References
- https://github.com/ziad626/extract-zip-security-research/security/advisories/GHSA-x7jf-2287-qcpf
- https://nvd.nist.gov/vuln/detail/CVE-2026-56876
- https://github.com/max-mapper/extract-zip
- https://raw.githubusercontent.com/cisagov/CSAF/develop/csaf_files/IT/white/2026/va-26-177-01.json
- https://www.cve.org/CVERecord?id=CVE-2026-56876
