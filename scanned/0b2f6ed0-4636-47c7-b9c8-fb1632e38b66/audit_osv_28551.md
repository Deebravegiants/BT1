# [M] Apache StreamPark IDOR Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2024-34457
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-22
Source: https://osv.dev/vulnerability/CVE-2024-34457
Type: osv

## Details
On versions before 2.1.4, after a regular user successfully logs in, they can manually make a request using the authorization token to view everyone's user flink information, including executeSQL and config.

Mitigation:

all users should upgrade to 2.1.4

## References
- http://www.openwall.com/lists/oss-security/2024/07/22/2
- https://www.openwall.com/lists/oss-security/2024/07/22/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/34xxx/CVE-2024-34457.json
- https://lists.apache.org/thread/brlfrmvw9dcv38zoofmhxg7qookmwn7j
- https://nvd.nist.gov/vuln/detail/CVE-2024-34457
