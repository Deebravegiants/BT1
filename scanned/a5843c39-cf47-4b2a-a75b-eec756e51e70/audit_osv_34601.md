# [H] Piwigo is vulnerable to one-click account takeover by modifying the password-reset link

## Summary
Severity: High
Advisory: CVE-2025-62406
Aliases: GHSA-9986-w7jf-33f6
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-62406
Type: osv

## Details
Piwigo is a full featured open source photo gallery application for the web. In Piwigo 15.6.0, using the password reset function allows sending a password-reset URL by entering an existing username or email address. However, the hostname used to construct this URL is taken from the HTTP request's Host header and is not validated at all. Therefore, an attacker can send a password-reset URL with a modified hostname to an existing user whose username or email the attacker knows or guesses. This issue has been patched in version 15.7.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62406.json
- https://github.com/Piwigo/Piwigo/security/advisories/GHSA-9986-w7jf-33f6
- https://nvd.nist.gov/vuln/detail/CVE-2025-62406
- https://github.com/Piwigo/Piwigo/commit/9d2565465efc3570963ff431b45cad21610f6692
