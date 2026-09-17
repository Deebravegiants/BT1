# [M] CVE-2021-40642

## Summary
Severity: Medium
Advisory: CVE-2021-40642
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2022-06-29
Source: https://osv.dev/vulnerability/CVE-2021-40642
Type: osv

## Details
Textpattern CMS v4.8.7 and older vulnerability exists through Sensitive Cookie in HTTPS Session Without 'Secure' Attribute via textpattern/lib/txplib_misc.php. The secure flag is not set for txp_login session cookie in the application. If the secure flag is not set, then the cookie will be transmitted in clear-text if the user visits any HTTP URLs within the cookie's scope. An attacker may be able to induce this event by feeding a user suitable links, either directly or via another web site.

## References
- https://www.huntr.dev/bounties/aadbe434-a376-443b-876f-2a1cbab7847b/
- https://github.com/textpattern/textpattern/commit/211fab0093999f59b0b61682aa988ac7d8337aa9
