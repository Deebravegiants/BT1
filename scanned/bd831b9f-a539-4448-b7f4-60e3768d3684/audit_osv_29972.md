# [C] CVE-2024-48176

## Summary
Severity: Critical
Advisory: CVE-2024-48176
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-48176
Type: osv

## Details
Lylme Spage v1.9.5 is vulnerable to Incorrect Access Control. There is no limit on the number of login attempts, and the verification code will not be refreshed after a failed login, which allows attackers to blast the username and password and log into the system backend.

## References
- https://gist.github.com/Gryffinbit/c0b37c6caae4844d4f59368e454d3e46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48176.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48176
