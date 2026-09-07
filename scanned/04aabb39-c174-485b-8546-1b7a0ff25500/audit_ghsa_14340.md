# [M] Uvdesk vulnerable to stored cross-site scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-fwhv-9phj-wrj5
CVE: CVE-2023-0325
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-05
Source: https://github.com/advisories/GHSA-fwhv-9phj-wrj5
Type: github-advisory

## Affected
- Packagist: `uvdesk/community-skeleton` — affected >=0

## Details
Uvdesk version 1.1.1 allows an unauthenticated remote attacker to exploit a stored XSS in the application. This is possible because the application does not correctly validate the message sent by the clients in the ticket.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-0325
- https://fluidattacks.com/advisories/labrinth
- https://github.com/uvdesk/community-skeleton
