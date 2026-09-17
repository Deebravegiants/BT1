# [C] Apache StreamPark: session not invalidated after logout

## Summary
Severity: Critical
Advisory: CVE-2024-29070
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-07-23
Source: https://osv.dev/vulnerability/CVE-2024-29070
Type: osv

## Details
On versions before 2.1.4, session is not invalidated after logout. When the user logged in successfully, the Backend service returns "Authorization" as the front-end authentication credential. "Authorization" can still initiate requests and access data even after logout.

Mitigation:

all users should upgrade to 2.1.4

## References
- http://www.openwall.com/lists/oss-security/2024/07/22/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/29xxx/CVE-2024-29070.json
- https://lists.apache.org/thread/zslblrz1l0n9t67mqdv42yv75ncfn9zl
- https://nvd.nist.gov/vuln/detail/CVE-2024-29070
