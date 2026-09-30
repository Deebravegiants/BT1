# [C] calibre: Arbitrary Code Execution in Template Formatter via Book Metadata

## Summary
Severity: Critical
Advisory: CVE-2026-53511
Aliases: GHSA-2j4m-2q7x-2c47
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-53511
Type: osv

## Details
calibre is an e-book manager. Prior to 9.10.0, a malicious EPUB, OPF, or PDF file can execute arbitrary Python code when its metadata is read by calibre, including through Add books or Edit books, by embedding a custom column definition with a python: template in calibre:user_metadata that is passed unsanitized to exec() in the template formatter. This issue is fixed in version 9.10.0.

## References
- https://github.com/kovidgoyal/calibre/releases/tag/v9.10.0
- https://lists.debian.org/debian-lts-announce/2026/08/msg00034.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53511.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-2j4m-2q7x-2c47
- https://nvd.nist.gov/vuln/detail/CVE-2026-53511
- https://github.com/kovidgoyal/calibre/commit/712f4e1ff5c1e798c335bef3bacc4efdee052e9c
