# [M] HotCRP vulnerable to exposure of submitted documents

## Summary
Severity: Medium
Advisory: CVE-2026-23878
Aliases: GHSA-vh3x-xwj4-jvqx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-19
Source: https://osv.dev/vulnerability/CVE-2026-23878
Type: osv

## Details
HotCRP is conference review software. Starting in commit aa20ef288828b04550950cf67c831af8a525f508 and prior to commit ceacd5f1476458792c44c6a993670f02c984b4a0, authors with at least one submission on a HotCRP site could use the document API to download any documents (PDFs, attachments) associated with any submission. The problem was patched in commit ceacd5f1476458792c44c6a993670f02c984b4a0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23878.json
- https://github.com/kohler/hotcrp/security/advisories/GHSA-vh3x-xwj4-jvqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-23878
- https://github.com/kohler/hotcrp/commit/aa20ef288828b04550950cf67c831af8a525f508
- https://github.com/kohler/hotcrp/commit/ceacd5f1476458792c44c6a993670f02c984b4a0
