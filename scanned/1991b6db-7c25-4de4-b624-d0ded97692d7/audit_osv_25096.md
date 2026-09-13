# [H] CVE-2023-30636

## Summary
Severity: High
Advisory: CVE-2023-30636
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-13
Source: https://osv.dev/vulnerability/CVE-2023-30636
Type: osv

## Details
TiKV 6.1.2 allows remote attackers to cause a denial of service (fatal error, with RpcStatus UNAVAILABLE for "not leader") upon an attempt to start a node in a situation where the context deadline is exceeded

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30636.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30636
- https://github.com/tikv/tikv/issues/14517
