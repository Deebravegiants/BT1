# [M] Apache CloudStack: Incomplete session invalidation on web interface logout

## Summary
Severity: Medium
Advisory: CVE-2024-45462
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2024-10-16
Source: https://osv.dev/vulnerability/CVE-2024-45462
Type: osv

## Details
The logout operation in the CloudStack web interface does not expire the user session completely which is valid until expiry by time or restart of the backend service. An attacker that has access to a user's browser can use an unexpired session to gain access to resources owned by the logged out user account. This issue affects Apache CloudStack from 4.15.1.0 through 4.18.2.3; and from 4.19.0.0 through 4.19.1.1.




Users are recommended to upgrade to Apache CloudStack 4.18.2.4 or 4.19.1.2, or later, which addresses this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/10/15/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45462.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45462
- https://cloudstack.apache.org/blog/security-release-advisory-4.18.2.4-4.19.1.2
- https://lists.apache.org/thread/ktsfjcnj22x4kg49ctock3d9tq7jnvlo
