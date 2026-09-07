# [M] Leantime allows Cross-Site Request Forgery (CSRF)

## Summary
Severity: Medium
Advisory: GHSA-92xh-6x7v-4rmq
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-02-21
Source: https://github.com/advisories/GHSA-92xh-6x7v-4rmq
Type: github-advisory

## Affected
- Packagist: `leantime/leantime` — affected >=0 <3.1.2

## Details
**CSRF**
### Summary
A cross-site request forgery vulnerability allows a remote actor to create an account with Owner privileges. By luring an Owner or Administrator into clicking a button on an attacker-controlled website, a request will be issued, generating an account with the attacker's information and role of their choosing. 

### Impact
While the likelihood of a successful exploit is low, the impact would be high as the attacker could then gain complete control over the victim's environment.

## References
- https://github.com/Leantime/leantime/security/advisories/GHSA-92xh-6x7v-4rmq
- https://github.com/Leantime/leantime
