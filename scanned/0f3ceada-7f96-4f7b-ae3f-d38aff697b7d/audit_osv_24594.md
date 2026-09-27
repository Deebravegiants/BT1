# [H] contiki-ng BLE-L2CAP contains Improper size validation of L2CAP frames

## Summary
Severity: High
Advisory: CVE-2023-23609
Aliases: GHSA-qr4q-6h3m-h3g7
CVSS: 8.2 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:L)
Published: 2023-01-25
Source: https://osv.dev/vulnerability/CVE-2023-23609
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for Next-Generation IoT devices. Versions prior to and including 4.8 are vulnerable to an out-of-bounds write that can occur in the BLE-L2CAP module. The Bluetooth Low Energy - Logical Link Control and Adaptation Layer Protocol (BLE-L2CAP) module handles fragmentation of packets up the configured MTU size. When fragments are reassembled, they are stored in a packet buffer of a configurable size, but there is no check to verify that the packet buffer is large enough to hold the reassembled packet. In Contiki-NG's default configuration, it is possible that an out-of-bounds write of up to 1152 bytes occurs. The vulnerability has been patched in the "develop" branch of Contiki-NG, and will be included in release 4.9. The problem can be fixed by applying the patch in Contiki-NG pull request #2254 prior to the release of version 4.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23609.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-qr4q-6h3m-h3g7
- https://nvd.nist.gov/vuln/detail/CVE-2023-23609
- https://github.com/contiki-ng/contiki-ng/pull/2254
