# [M] COVESA Open1722 0.9.2 Stack Memory Disclosure via acf-can-listener.c Integer Truncation

## Summary
Severity: Medium
Advisory: CVE-2026-73523
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-73523
Type: osv

## Details
COVESA Open1722 through 0.9.2 contains an integer truncation vulnerability in acf-can-listener.c that allows unauthenticated remote attackers to cause the CAN listener to transmit process stack memory onto the CAN bus by sending a rejected UDP datagram with a matching AVTP stream ID. The num_can_msgs variable declared as uint8_t truncates the -1 error return value from avtp_to_can() to 255, causing a write loop to iterate 255 times over a 15-slot stack array and leak approximately 18 KB of adjacent stack memory as roughly 240 CAN frames to any recipient on the CAN bus.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73523.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-73523
- https://www.vulncheck.com/advisories/covesa-open1722-stack-memory-disclosure-via-acf-can-listener-c-integer-truncation
- https://github.com/COVESA/Open1722/issues/154
- https://github.com/COVESA/Open1722
