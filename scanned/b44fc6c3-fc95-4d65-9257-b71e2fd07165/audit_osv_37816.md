# [H] CVE-2026-33373

## Summary
Severity: High
Advisory: CVE-2026-33373
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33373
Type: osv

## Details
An issue was discovered in Zimbra Collaboration (ZCS) 10.0 and 10.1. A Cross-Site Request Forgery (CSRF) vulnerability exists in Zimbra Web Client due to the issuance of authentication tokens without CSRF protection during certain account state transitions. Specifically, tokens generated after operations such as enabling two-factor authentication or changing a password may lack CSRF enforcement. While such a token is active, authenticated SOAP requests that trigger token generation or state changes can be performed without CSRF validation. An attacker could exploit this by inducing a victim to submit crafted requests, potentially allowing sensitive account actions such as disabling two-factor authentication. The issue is mitigated by ensuring CSRF protection is consistently enforced for all issued authentication tokens.

## References
- https://wiki.zimbra.com/wiki/Security_Center
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.0.18#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Releases/10.1.13#Security_Fixes
- https://wiki.zimbra.com/wiki/Zimbra_Responsible_Disclosure_Policy
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33373.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-33373
