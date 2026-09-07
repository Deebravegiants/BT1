# [M] Mautic vulnerable to reflected XSS in lead:addLeadTags - Quick Add

## Summary
Severity: Medium
Advisory: GHSA-9v8p-m85m-f7mm
CVE: CVE-2025-9823
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-03
Source: https://github.com/advisories/GHSA-9v8p-m85m-f7mm
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=4.4.0 <4.4.17
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.8
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.5

## Details
## Summary

A Cross-Site Scripting (XSS) vulnerability allows an attacker to execute arbitrary JavaScript in the context of another user’s session. This occurs because user-supplied input is reflected back in the server’s response without proper sanitization or escaping, potentially enabling malicious actions such as session hijacking, credential theft, or unauthorized actions in the application.

## Details

The vulnerability resides in the “Tags” input field on the /s/ajax?action=lead:addLeadTags endpoint. Although the server applies sanitization before storing the data or returning it later, the payload is executed immediately in the victim’s browser upon reflection, allowing an attacker to run arbitrary JavaScript in the user’s session.

## Impact
A Reflected XSS attack can have a significant impact, allowing attackers to steal sensitive user data like cookies, redirect users to malicious websites, manipulate the web page content, and essentially take control of a user's session within an application by executing malicious JavaScript code within the victim's browser, even if the server-side code is secure; essentially enabling them to perform actions as if they were the logged-in user.

## References
- [Web Security Academy: Cross-site scripting](https://portswigger.net/web-security/cross-site-scripting)
- [Web Security Academy: Reflected cross-site scripting](https://portswigger.net/web-security/cross-site-scripting/reflected)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-9v8p-m85m-f7mm
- https://nvd.nist.gov/vuln/detail/CVE-2025-9823
- https://github.com/mautic/mautic
