# [H] CVE-2025-51741

## Summary
Severity: High
Advisory: CVE-2025-51741
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-51741
Type: osv

## Details
An issue was discovered in Veal98 Echo Open-Source Community System 2.2 thru 2.3 allowing an unauthenticated attacker to cause the server to send email verification messages to arbitrary users via the /sendEmailCodeForResetPwd endpoint potentially causing a denial of service to the server or the downstream users.

## References
- https://gist.github.com/Paxsizy/9d92e8746778cf0926705d89b4f3618c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51741.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51741
- https://github.com/Veal98/Echo
