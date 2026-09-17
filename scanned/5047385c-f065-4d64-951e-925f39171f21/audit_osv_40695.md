# [M] nanoMODBUS Off-by-One Buffer Overflow in recv_msg_header() via Crafted MBAP Length Field

## Summary
Severity: Medium
Advisory: CVE-2026-54410
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N/E:P/AU:Y)
Published: 2026-06-14
Source: https://osv.dev/vulnerability/CVE-2026-54410
Type: osv

## Details
nanoMODBUS through v1.23.0 contains an off-by-one buffer overflow in the recv_msg_header function of the Modbus/TCP server that allows remote unauthenticated attackers to write one attacker-controlled byte past the end of the 260-byte receive buffer by sending a crafted MBAP frame whose Length field is set to 255.

## References
- https://github.com/debevv/nanoMODBUS/blob/v1.23.0/nanomodbus.c#L369
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54410.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54410
- https://github.com/debevv/nanoMODBUS
- https://cwe.mitre.org/data/definitions/193.html
- https://cwe.mitre.org/data/definitions/787.html
