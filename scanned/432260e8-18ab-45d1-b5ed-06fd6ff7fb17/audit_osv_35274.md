# [M] CVE-2025-70129

## Summary
Severity: Medium
Advisory: CVE-2025-70129
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-03-10
Source: https://osv.dev/vulnerability/CVE-2025-70129
Type: osv

## Details
If the anti spam-captcha functionality in PluXml versions 5.8.22 and earlier is enabled, a captcha challenge is generated with a format that can be automatically recognized for articles, such that an automated script is able to solve this anti-spam mechanism trivially and publish spam comments. The details of captcha challenge are exposed within document body of articles with comments & anti spam-captcha functionalities enabled, including "capcha-letter", "capcha-word" and "capcha-token" which can be used to construct a valid post request to publish a comment. As such, attackers can flood articles with automated spam comments, especially if there are no other web defenses available.

## References
- https://github.com/forest4x/vuln-research-public/blob/main/CVE-2025-70129.pdf
- https://youtu.be/dD2olE4yMqY
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/70xxx/CVE-2025-70129.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-70129
