# [C] calibre is vulnerable to arbitrary code execution when opening FB2 files

## Summary
Severity: Critical
Advisory: CVE-2025-64486
Aliases: GHSA-hpwq-c98h-xp8g
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-64486
Type: osv

## Details
calibre is an e-book manager. In versions 8.13.0 and prior, calibre does not validate filenames when handling binary assets in FB2 files, allowing an attacker to write arbitrary files on the filesystem when viewing or converting a malicious FictionBook file. This can be leveraged to achieve arbitrary code execution. This issue is fixed in version 8.14.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64486.json
- https://github.com/kovidgoyal/calibre/security/advisories/GHSA-hpwq-c98h-xp8g
- https://nvd.nist.gov/vuln/detail/CVE-2025-64486
- https://github.com/kovidgoyal/calibre/commit/6f94bce214bf7d43c829804db3741afa5e83c0c5
