# [H] Apache StreamPark (incubating): Unchecked SQL query fields trigger SQL injection vulnerability

## Summary
Severity: High
Advisory: CVE-2023-52290
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2023-52290
Type: osv

## Details
In streampark-console the list pages(e.g: application pages), users can sort page by field. This sort field is sent from the front-end to the back-end, and the SQL query is generated using this field. However, because this sort field isn't validated, there is a risk of SQL injection vulnerability. The attacker must successfully log into the system to launch an attack, which may cause data leakage. Since no data will be written, so this is a low-impact vulnerability.

Mitigation:

all users should upgrade to 2.1.4,  Such parameters will be blocked.

## References
- http://www.openwall.com/lists/oss-security/2024/07/15/4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52290.json
- https://lists.apache.org/thread/t3mcm8pb65d9gj3wrgtj9sx9s2pfvvl3
- https://nvd.nist.gov/vuln/detail/CVE-2023-52290
