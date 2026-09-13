# [H] Pigeon has a Host Header Injection in email verification flow

## Summary
Severity: High
Advisory: CVE-2026-32616
Aliases: GHSA-rrj4-9wgq-prcr
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-32616
Type: osv

## Details
Pigeon is a message board/notepad/social system/blog. Prior to 1.0.201, the application uses $_SERVER['HTTP_HOST'] without validation to construct email verification URLs in the register and resendmail flows. An attacker can manipulate the Host header in the HTTP request, causing the verification link sent to the user's email to point to an attacker-controlled domain. This can lead to account takeover by stealing the email verification token. This vulnerability is fixed in 1.0.201.

## References
- https://github.com/kasuganosoras/Pigeon/releases/tag/1.0.201
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32616.json
- https://github.com/kasuganosoras/Pigeon/security/advisories/GHSA-rrj4-9wgq-prcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-32616
