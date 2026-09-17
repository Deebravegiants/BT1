# [C] CVE-2022-46478

## Summary
Severity: Critical
Advisory: CVE-2022-46478
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-13
Source: https://osv.dev/vulnerability/CVE-2022-46478
Type: osv

## Details
The RPC interface in datax-web v1.0.0 and v2.0.0 to v2.1.2 contains no permission checks by default which allows attackers to execute arbitrary commands via crafted Hessian serialized data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/46xxx/CVE-2022-46478.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-46478
- https://github.com/WeiYe-Jing/datax-web/issues/587
