# [M] Apache CloudStack: Unauthorised template/ISO list access to the domain/resource admins

## Summary
Severity: Medium
Advisory: CVE-2025-30675
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-06-10
Source: https://osv.dev/vulnerability/CVE-2025-30675
Type: osv

## Details
In Apache CloudStack, a flaw in access control affects the listTemplates and listIsos APIs. A malicious Domain Admin or Resource Admin can exploit this issue by intentionally specifying the 'domainid' parameter along with the 'filter=self' or 'filter=selfexecutable' values. This allows the attacker to gain unauthorized visibility into templates and ISOs under the ROOT domain.

A malicious admin can enumerate and extract metadata of templates and ISOs that belong to unrelated domains, violating isolation boundaries and potentially exposing sensitive or internal configuration details. 

This vulnerability has been fixed by ensuring the domain resolution strictly adheres to the caller's scope rather than defaulting to the ROOT domain.




Affected users are recommended to upgrade to Apache CloudStack 4.19.3.0 or 4.20.1.0.

## References
- https://cloudstack.apache.org/blog/cve-advisories-4.19.3.0-4.20.1.0/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30675.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-30675
- https://www.shapeblue.com/shapeblue-security-advisory-apache-cloudstack-security-releases-4-19-3-0-and-4-20-1-0/
- https://lists.apache.org/thread/y3qnwn59t8qggtdohv7k7vw39bgb3d60
