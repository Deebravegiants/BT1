# [M] Out-of-bounds read when decompressing UDP header

## Summary
Severity: Medium
Advisory: CVE-2022-36052
Aliases: GHSA-vwr8-6mqv-x7f5
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-36052
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for Next-Generation IoT devices. The 6LoWPAN implementation in Contiki-NG may cast a UDP header structure at a certain offset in a packet buffer. The code does not check whether the packet buffer is large enough to fit a full UDP header structure from the offset where the casting is made. Hence, it is possible to cause an out-of-bounds read beyond the packet buffer. The problem affects anyone running devices with Contiki-NG versions previous to 4.8, and which may receive 6LoWPAN packets from external parties. The problem has been patched in Contiki-NG version 4.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36052.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-vwr8-6mqv-x7f5
- https://nvd.nist.gov/vuln/detail/CVE-2022-36052
- https://github.com/contiki-ng/contiki-ng/pull/1648
