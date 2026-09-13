# [M] CVE-2022-3165

## Summary
Severity: Medium
Advisory: CVE-2022-3165
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-17
Source: https://osv.dev/vulnerability/CVE-2022-3165
Type: osv

## Details
An integer underflow issue was found in the QEMU VNC server while processing ClientCutText messages in the extended format. A malicious client could use this flaw to make QEMU unresponsive by sending a specially crafted payload message, resulting in a denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3165.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/I36LKZA7Z65J3LJU2P37LVTWDFTXBMPU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZTY7TVHX62OJWF6IOBCIGLR2N5K4QN3E/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3165
- https://security.netapp.com/advisory/ntap-20221223-0006/
- https://gitlab.com/qemu-project/qemu/-/commit/d307040b18
