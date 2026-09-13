# [H] Header Poisoning in Raytha CMS

## Summary
Severity: High
Advisory: CVE-2025-69240
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2025-69240
Type: osv

## Details
Raytha CMS allows an attacker to spoof `X-Forwarded-Host` or `Host` headers to attacker controlled domain. The attacker (who knows the victim's email address) can force the server to send an email with password reset link pointing to the domain from spoofed header. When victim clicks the link, browser sends request to the attacker’s domain with the token in the path allowing the attacker to capture the token. This allows the attacker to reset victim's password and take over the victim's account.

This issue was fixed in version 1.4.6.

## References
- https://raytha.com
- https://cert.pl/en/posts/2026/03/CVE-2025-69236
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69240.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69240
- https://github.com/raythahq/raytha
