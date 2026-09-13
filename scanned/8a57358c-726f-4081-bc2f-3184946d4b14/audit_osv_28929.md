# [C] Apache CloudStack: Unauthenticated cluster service port leads to remote execution

## Summary
Severity: Critical
Advisory: CVE-2024-38346
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-05
Source: https://osv.dev/vulnerability/CVE-2024-38346
Type: osv

## Details
The CloudStack cluster service runs on unauthenticated port (default 9090) that can be misused to run arbitrary commands on targeted hypervisors and CloudStack management server hosts. Some of these commands were found to have command injection vulnerabilities that can result in arbitrary code execution via agents on the hosts that may run as a privileged user. An attacker that can reach the cluster service on the unauthenticated port (default 9090), can exploit this to perform remote code execution on CloudStack managed hosts and result in complete compromise of the confidentiality, integrity, and availability of CloudStack managed infrastructure.

Users are recommended to restrict the network access to the cluster service port (default 9090) on a CloudStack management server host to only its peer CloudStack management server hosts. Users are recommended to upgrade to version 4.18.2.1, 4.19.0.2 or later, which addresses this issue.

## References
- http://www.openwall.com/lists/oss-security/2024/07/05/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38346.json
- https://lists.apache.org/thread/6l51r00csrct61plkyd3qg3fj99215d1
- https://nvd.nist.gov/vuln/detail/CVE-2024-38346
- https://www.shapeblue.com/shapeblue-security-advisory-apache-cloudstack-security-releases-4-18-2-1-and-4-19-0-2/
- https://cloudstack.apache.org/blog/security-release-advisory-4.19.0.2-4.18.2.1
