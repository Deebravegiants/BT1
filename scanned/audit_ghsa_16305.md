# [H] Statmic CMS vulnerable to account takeover via XSS and password reset link

## Summary
Severity: High
Advisory: GHSA-vqxq-hvxw-9mv9
CVE: CVE-2024-24570
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2024-02-01
Source: https://github.com/advisories/GHSA-vqxq-hvxw-9mv9
Type: github-advisory

## Affected
- Packagist: `statamic/cms` — affected >=4.00 <4.46.0
- Packagist: `statamic/cms` — affected >=0 <3.4.17

## Details
### Impact

HTML files crafted to look like jpg files are able to be uploaded, allowing for XSS.

This affects:

- front-end forms with asset fields without any mime type validation
- asset fields in the control panel
- asset browser in the control panel

Additionally, if the XSS is crafted in a specific way, the "copy password reset link" feature may be exploited to gain access to a user's password reset token and gain access to their account. The authorized user is required to execute the XSS in order for the vulnerability to occur.

### Patches

In versions 4.46.0 and 3.4.17, the XSS vulnerability has been patched, and the copy password reset link functionality has been disabled. (Users may still trigger password reset emails.)

### Credits

Statamic thanks Niklas Schilling (discovery, analysis, coordination) from the SEC Consult Vulnerability Lab (https://www.sec-consult.com/) for responsibly reporting the identified issues and working with us as we addressed them.

## References
- https://github.com/statamic/cms/security/advisories/GHSA-vqxq-hvxw-9mv9
- https://nvd.nist.gov/vuln/detail/CVE-2024-24570
- https://github.com/statamic/cms
- http://packetstormsecurity.com/files/177133/Statamic-CMS-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2024/Feb/17
