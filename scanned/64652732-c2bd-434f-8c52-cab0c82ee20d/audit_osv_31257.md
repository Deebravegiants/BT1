# [M] Admin Can Escalate Privileges to SuperAdmin Using Manual PUT Request

## Summary
Severity: Medium
Advisory: CVE-2024-6908
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:H/UI:P/VC:L/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2024-07-19
Source: https://osv.dev/vulnerability/CVE-2024-6908
Type: osv

## Details
Improper privilege management in Yugabyte Platform allows authenticated admin users to escalate privileges to SuperAdmin via a crafted PUT HTTP request, potentially leading to unauthorized access to sensitive system functions and data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6908.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6908
- https://github.com/yugabyte/yugabyte-db/commit/03b193de40b79329439bb9968a7d27a1cc57d662
- https://github.com/yugabyte/yugabyte-db/commit/68f01680c565be2a370cfb7734a1b3721d6778bb
