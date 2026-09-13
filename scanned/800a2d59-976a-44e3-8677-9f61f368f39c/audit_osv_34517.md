# [H] CVE-2025-61541

## Summary
Severity: High
Advisory: CVE-2025-61541
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-10-16
Source: https://osv.dev/vulnerability/CVE-2025-61541
Type: osv

## Details
Webmin 2.510 is vulnerable to a Host Header Injection in the password reset functionality (forgot_send.cgi). The reset link sent to users is constructed using the HTTP Host header via get_webmin_email_url(). An attacker can manipulate the Host header to inject a malicious domain into the reset email. If a victim follows the poisoned link, the attacker can intercept the reset token and gain full control of the target account.

## References
- http://www.webmin.com/
- https://github.com/bugdotexe/Vulnerability-Research/tree/main/CVE-2025-61541
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61541.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-61541
- https://github.com/webmin/webmin
