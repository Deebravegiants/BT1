# [M]  Decidim::Admin vulnerable to cross-site scripting (XSS) in the admin panel with QuillJS WYSWYG editor

## Summary
Severity: Medium
Advisory: GHSA-vvqw-fqwx-mqmm
CVE: CVE-2024-39910
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-09-16
Source: https://github.com/advisories/GHSA-vvqw-fqwx-mqmm
Type: github-advisory

## Affected
- RubyGems: `decidim` — affected >=0 <0.27.7

## Details
### Impact

The WYSWYG editor QuillJS is subject to potential XSS attach in case the attacker manages to modify the HTML before being uploaded to the server.

The attacker is able to change e.g. to <svg onload=alert('XSS')> if they know how to craft these requests themselves. 

### Patches

N/A

### Workarounds

Review the user accounts that have access to the admin panel (i.e. general Administrators, and participatory space's Administrators) and remove access to them if they don't need it. 

Disable the "Enable rich text editor for participants" setting in the admin dashboard

### References

OWASP ASVS v4.0.3-5.1.3

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-vvqw-fqwx-mqmm
- https://nvd.nist.gov/vuln/detail/CVE-2024-39910
- https://github.com/decidim/decidim/commit/47adca81cabea898005ec07b130b008f2a2be99f
- https://github.com/decidim/decidim
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/decidim/CVE-2024-39910.yml
