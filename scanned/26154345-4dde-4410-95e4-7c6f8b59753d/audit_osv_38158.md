# [M] OpenPrinting CUPS: Shared PostScript queue lets anonymous Print-Job requests reach `lp` code execution over the network

## Summary
Severity: Medium
Advisory: CVE-2026-34980
Aliases: GHSA-4852-v58g-6cwf
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:L/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-34980
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, in a network-exposed cupsd with a shared target queue, an unauthorized client can send a Print-Job to that shared PostScript queue without authentication. The server accepts a page-border value supplied as textWithoutLanguage, preserves an embedded newline through option escaping and reparse, and then reparses the resulting second-line PPD: text as a trusted scheduler control record. A follow-up raw print job can therefore make the server execute an attacker-chosen existing binary such as /usr/bin/vim as lp. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34980.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-4852-v58g-6cwf
- https://nvd.nist.gov/vuln/detail/CVE-2026-34980
