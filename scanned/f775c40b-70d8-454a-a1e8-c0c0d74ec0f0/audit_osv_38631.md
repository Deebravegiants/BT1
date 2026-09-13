# [M] OpenPrinting CUPS: Heap out-of-bounds read in SNMP supply-level polling leaks stack memory to authenticated users

## Summary
Severity: Medium
Advisory: CVE-2026-41079
Aliases: GHSA-6wpw-g8g6-wvrv
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41079
Type: osv

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. Prior to 2.4.17, a network-adjacent attacker can send a crafted SNMP response to the CUPS SNMP backend that causes an out-of-bounds read of up to 176 bytes past a stack buffer. The leaked memory is converted from UTF-16 to UTF-8 and stored as printer supply description strings, which are subsequently visible to authenticated users via IPP Get-Printer-Attributes responses and the CUPS web interface. This vulnerability is fixed in 2.4.17.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41079.json
- https://github.com/OpenPrinting/cups/security/advisories/GHSA-6wpw-g8g6-wvrv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41079
- https://github.com/OpenPrinting/cups/commit/b7c2525a885f528d243c3a92197ca99609b3f080
- https://github.com/OpenPrinting/cups/commit/d7fe0f521ff3b24676511e747b058362b9a20737
