# [H] Unchecked Download size in Uboot

## Summary
Severity: High
Advisory: CVE-2022-2347
CVSS: 7.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-2347
Type: osv

## Details
There exists an unchecked length field in UBoot. The U-Boot DFU implementation does not bound the length field in USB DFU download setup packets, and it does not verify that the transfer direction corresponds to the specified command. Consequently, if a physical attacker crafts a USB DFU download setup packet with a `wLength` greater than 4096 bytes, they can write beyond the heap-allocated request buffer.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00001.html
- https://seclists.org/oss-sec/2022/q3/41
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/2xxx/CVE-2022-2347.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-2347
