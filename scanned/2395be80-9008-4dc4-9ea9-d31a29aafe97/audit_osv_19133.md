# [M] CVE-2020-8138

## Summary
Severity: Medium
Advisory: CVE-2020-8138
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2020-8138
Type: osv

## Details
A missing check for IPv4 nested inside IPv6 in Nextcloud server < 17.0.1, < 16.0.7, and < 15.0.14 allowed a Server-Side Request Forgery (SSRF) vulnerability when subscribing to a malicious calendar URL.

## References
- https://nextcloud.com/security/advisory/?id=NC-SA-2020-014
- https://hackerone.com/reports/736867
