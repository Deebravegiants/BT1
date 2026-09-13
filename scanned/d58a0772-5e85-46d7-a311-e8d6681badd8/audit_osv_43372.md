# [M] COVESA Open1722 0.9.2 Stack Buffer Overflow via avtp_to_can() in acf-can-listener

## Summary
Severity: Medium
Advisory: CVE-2026-73522
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-73522
Type: osv

## Details
COVESA Open1722 through 0.9.2 contains a stack buffer overflow vulnerability that allows unauthenticated remote attackers to write past the end of a fixed 15-slot stack array by sending a crafted UDP datagram containing more than 15 ACF-CAN messages. The avtp_to_can() function increments its write index without bounding it against the caller-supplied array size, and because the listener accepts datagrams from any sender matching a hardcoded unauthenticated stream ID transmitted in plaintext, attackers can corrupt adjacent stack memory to achieve arbitrary code execution or denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73522
- https://www.vulncheck.com/advisories/covesa-open1722-stack-buffer-overflow-via-avtp-to-can-in-acf-can-listener
- https://github.com/COVESA/Open1722/issues/154
- https://github.com/COVESA/Open1722
