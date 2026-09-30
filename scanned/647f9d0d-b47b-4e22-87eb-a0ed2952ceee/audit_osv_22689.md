# [M] Exim DMARC dmarc.c dmarc_dns_lookup use after free

## Summary
Severity: Medium
Advisory: CVE-2022-3620
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2022-10-20
Source: https://osv.dev/vulnerability/CVE-2022-3620
Type: osv

## Details
A vulnerability was found in Exim and classified as problematic. This issue affects the function dmarc_dns_lookup of the file dmarc.c of the component DMARC Handler. The manipulation leads to use after free. The attack may be initiated remotely. The name of the patch is 12fb3842f81bcbd4a4519d5728f2d7e0e3ca1445. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-211919.

## References
- https://git.exim.org/exim.git/commit/12fb3842f81bcbd4a4519d5728f2d7e0e3ca1445
- https://vuldb.com/?id.211919
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3620.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/667V3ADXQ2MHUJMSXA3VZZEWLVSCIBEU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EIH4W5R7SHTUEQFWWKB4TUO5YFZX64KV/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XV2K2AWF62FSJ64B5CUZPFT4COK7P5PM/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3620
