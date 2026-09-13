# [M] OpenPrinting CUPS: Heap overflow in `get_options()`

## Summary
Severity: Medium
Advisory: CVE-2026-34979
Aliases: GHSA-6qxf-7jx6-86fh
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34979
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, there is a heap-based buffer overflow in the CUPS scheduler when building filter option strings from job attribute. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34979.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-6qxf-7jx6-86fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34979
