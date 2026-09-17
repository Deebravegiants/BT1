# [C] CVE-2022-37434

## Summary
Severity: Critical
Advisory: CVE-2022-37434
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-05
Source: https://osv.dev/vulnerability/CVE-2022-37434
Type: osv

## Details
zlib through 1.2.12 has a heap-based buffer over-read or buffer overflow in inflate in inflate.c via a large gzip header extra field. NOTE: only applications that call inflateGetHeader are affected. Some common applications bundle the affected zlib source code but may be unable to call inflateGetHeader (e.g., see the nodejs/node reference).

## References
- https://cert-portal.siemens.com/productcert/html/ssa-150063.html
- https://cert-portal.siemens.com/productcert/html/ssa-202008.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://cert-portal.siemens.com/productcert/html/ssa-470355.html
- https://cert-portal.siemens.com/productcert/html/ssa-561322.html
- https://github.com/madler/zlib/blob/21767c654d31d2dccdde4330529775c6c5fd5389/zlib.h#L1062-L1063
- https://github.com/nodejs/node/blob/75b68c6e4db515f76df73af476eccf382bbcb00a/deps/zlib/inflate.c#L762-L764
- https://support.apple.com/kb/HT213488
- https://support.apple.com/kb/HT213489
- https://support.apple.com/kb/HT213490
- https://support.apple.com/kb/HT213491
- https://support.apple.com/kb/HT213493
- https://support.apple.com/kb/HT213494
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37434.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JWN4VE3JQR4O2SOUS5TXNLANRPMHWV4I/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NMBOJ77A7T7PQCARMDUK75TE6LLESZ3O/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PAVPQNCG3XRLCLNSQRM3KAN5ZFMVXVTY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X5U7OTKZSHY2I3ZFJSR2SHFHW72RKGDK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YRQAI7H4M4RQZ2IWZUEEXECBE5D56BH2/
- https://nvd.nist.gov/vuln/detail/CVE-2022-37434
