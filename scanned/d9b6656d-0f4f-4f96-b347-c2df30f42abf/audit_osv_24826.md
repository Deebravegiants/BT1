# [M] CVE-2023-27294

## Summary
Severity: Medium
Advisory: CVE-2023-27294
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-27294
Type: osv

## Details
Improper neutralization of input during web page generation allows an authenticated attacker with access to a restricted account to submit malicious Javascript as the description for a calendar event, which would then be executed in other users' browsers if they browse to that event. This could result in stealing session tokens from users with higher permission levels or forcing users to make actions without their knowledge.

## References
- https://www.tenable.com/security/research/tra-2023-8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27294.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27294
