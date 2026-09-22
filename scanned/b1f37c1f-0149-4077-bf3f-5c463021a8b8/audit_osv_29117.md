# [C] Apache CloudStack: Integration API service uses dynamic port when disabled

## Summary
Severity: Critical
Advisory: CVE-2024-39864
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-39864
Type: osv

## Details
The CloudStack integration API service allows running its unauthenticated API server (usually on port 8096 when configured and enabled via integration.api.port global setting) for internal portal integrations and for testing purposes. By default, the integration API service port is disabled and is considered disabled when integration.api.port is set to 0 or negative. Due to an improper initialisation logic, the integration API service would listen on a random port when its port value is set to 0 (default value). An attacker that can access the CloudStack management network could scan and find the randomised integration API service port and exploit it to perform unauthorised administrative actions and perform remote code execution on CloudStack managed hosts and result in complete compromise of the confidentiality, integrity, and availability of CloudStack managed infrastructure.

Users are recommended to restrict the network access on the CloudStack management server hosts to only essential ports. Users are recommended to upgrade to version 4.18.2.1, 4.19.0.2 or later, which addresses this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/07/05/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/39xxx/CVE-2024-39864.json
- https://lists.apache.org/thread/6l51r00csrct61plkyd3qg3fj99215d1
- https://nvd.nist.gov/vuln/detail/CVE-2024-39864
- https://www.shapeblue.com/shapeblue-security-advisory-apache-cloudstack-security-releases-4-18-2-1-and-4-19-0-2/
- https://cloudstack.apache.org/blog/security-release-advisory-4.19.0.2-4.18.2.1
