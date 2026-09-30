# [H] Buffer overflow in L2CAP due to misconfigured MTU

## Summary
Severity: High
Advisory: CVE-2023-28116
Aliases: GHSA-m737-4vx6-pfqp
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-17
Source: https://osv.dev/vulnerability/CVE-2023-28116
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for internet of things (IoT) devices. In versions 4.8 and prior, an out-of-bounds write can occur in the BLE L2CAP module of the Contiki-NG operating system.  The network stack of Contiki-NG uses a global buffer (packetbuf) for processing of packets, with the size of PACKETBUF_SIZE. In particular, when using the BLE L2CAP module with the default configuration, the PACKETBUF_SIZE value becomes larger then the actual size of the packetbuf.  When large packets are processed by the L2CAP module, a buffer overflow can therefore occur when copying the packet data to the packetbuf. The vulnerability has been patched in the "develop" branch of Contiki-NG, and will be included in release 4.9. The problem can be worked around by applying the patch manually.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28116.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-m737-4vx6-pfqp
- https://nvd.nist.gov/vuln/detail/CVE-2023-28116
- https://github.com/contiki-ng/contiki-ng/pull/2398
