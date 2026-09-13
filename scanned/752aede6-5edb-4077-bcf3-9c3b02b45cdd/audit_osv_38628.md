# [M] RT: Spreadsheet downloads vulnerable to CSV/formula injection in Microsoft Excel and similar apps

## Summary
Severity: Medium
Advisory: CVE-2026-41073
Aliases: GHSA-6x92-7v65-7m3r
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-41073
Type: osv

## Details
RT is an open source, enterprise-grade issue and ticket tracking system. Versions prior to 5.0.10 and 6.0.0 through 6.0.2 contain a spreadsheet (CSV/formula) injection vulnerability. User-controlled data in spreadsheet exports is not sanitized before being written to the output file, which can cause spreadsheet applications to interpret crafted values as formulas or macros when the file is opened. This issue has been fixed in versions 5.0.10 and 6.0.3. If developers are unable to upgrade immediately, they can temporarily work around this issue by avoiding opening exported RT spreadsheet files directly in spreadsheet applications when the data may contain untrusted user input.

## References
- https://github.com/bestpractical/rt/releases/tag/rt-5.0.10
- https://github.com/bestpractical/rt/releases/tag/rt-6.0.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41073.json
- https://github.com/bestpractical/rt/security/advisories/GHSA-6x92-7v65-7m3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41073
