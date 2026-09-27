# [M] Out-of-bounds read in the uIP buffer module

## Summary
Severity: Medium
Advisory: CVE-2022-36053
Aliases: GHSA-2j9c-7754-w4cw
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-36053
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for Next-Generation IoT devices. The low-power IPv6 network stack of Contiki-NG has a buffer module (os/net/ipv6/uipbuf.c) that processes IPv6 extension headers in incoming data packets. As part of this processing, the function uipbuf_get_next_header casts a pointer to a uip_ext_hdr structure into the packet buffer at different offsets where extension headers are expected to be found, and then reads from this structure. Because of a lack of bounds checking, the casting can be done so that the structure extends beyond the packet's end. Hence, with a carefully crafted packet, it is possible to cause the Contiki-NG system to read data outside the packet buffer. A patch that fixes the vulnerability is included in Contiki-NG 4.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36053.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-2j9c-7754-w4cw
- https://nvd.nist.gov/vuln/detail/CVE-2022-36053
- https://github.com/contiki-ng/contiki-ng/pull/1648
