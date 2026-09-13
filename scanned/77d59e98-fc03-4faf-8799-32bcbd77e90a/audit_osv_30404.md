# [M] data.all admin user may access potentially sensitive data stored by producers via logs

## Summary
Severity: Medium
Advisory: CVE-2024-52314
Aliases: GHSA-p2h8-r28g-5q6h
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-52314
Type: osv

## Details
A data.all admin team member who has access to the customer-owned AWS Account where data.all is deployed may be able to extract user data from data.all application logs in data.all via CloudWatch log scanning for particular operations that interact with customer producer teams data.

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2024-013
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52314.json
- https://github.com/data-dot-all/dataall/security/advisories/GHSA-p2h8-r28g-5q6h
- https://nvd.nist.gov/vuln/detail/CVE-2024-52314
- https://github.com/data-dot-all/dataall/releases/tag/v2.6.1
