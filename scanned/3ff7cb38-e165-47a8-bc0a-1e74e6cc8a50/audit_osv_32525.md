# [H] Apache Traffic Server: Client IP address from PROXY protocol is not used for ACL

## Summary
Severity: High
Advisory: CVE-2025-31698
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-31698
Type: osv

## Details
ACL configured in ip_allow.config or remap.config does not use IP addresses that are provided by PROXY protocol.

Users can use a new setting (proxy.config.acl.subjects) to choose which IP addresses to use for the ACL if Apache Traffic Server is configured to accept PROXY protocol. 
This issue affects undefined: from 10.0.0 through 10.0.6, from 9.0.0 through 9.2.10.

Users are recommended to upgrade to version 9.2.11 or 10.0.6, which fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31698.json
- https://lists.apache.org/thread/15t32nxbypqg1m2smp640vjx89o6v5f8
- https://nvd.nist.gov/vuln/detail/CVE-2025-31698
