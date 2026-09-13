# [H] CVE-2023-30637

## Summary
Severity: High
Advisory: CVE-2023-30637
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-13
Source: https://osv.dev/vulnerability/CVE-2023-30637
Type: osv

## Details
Baidu braft 1.1.2 has a memory leak related to use of the new operator in example/atomic/atomic_server. NOTE: installations with brpc-0.14.0 and later are unaffected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30637.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30637
- https://github.com/baidu/braft/issues/393
