# [M] Improper Access Control (IDOR) vulnerability in Graylog Web Interface

## Summary
Severity: Medium
Advisory: CVE-2026-1436
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-1436
Type: osv

## Details
Improper Access Control (IDOR) in the Graylog API, version 2.2.3, which occurs when modifying the user ID in the URL. An authenticated user can access other user's profiles without proper authorization checks. Exploiting this vulnerability allows valid users of the system to be listed and sensitive third-party information to be accessed, such as names, email addresses, internal identifiers, and last activity. The endpoint 'http://<IP>:12900/users/<my_user>' does not implement object-level authorization validations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1436.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-1436
- https://www.incibe.es/en/incibe-cert/notices/aviso/multiple-vulnerabilities-graylog
