# [M] Decidim: HTML content blocks allow stored script execution

## Summary
Severity: Medium
Advisory: GHSA-533c-2vh9-4r86
CVE: CVE-2026-45572
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-533c-2vh9-4r86
Type: github-advisory

## Affected
- RubyGems: `decidim-core` — affected >=0 <0.30.9
- RubyGems: `decidim-core` — affected >=0.31.0.rc1 <0.31.5
- RubyGems: `decidim-core` — affected >=0.32.0.rc1 <0.32.0

## Details
## Description
 
A privileged admin user who can edit an affected landing page can store arbitrary HTML/JavaScript in an `HTML block`, and the public page renders it with `html_safe` and no output escaping.

## Technical description
    
This issue lets any admin who can edit an affected landing page store arbitrary HTML and JavaScript in an `HTML block`. The block is then rendered back through `Decidim::ContentBlocks::HtmlCell#html_content` without a sanitization boundary, so the script executes later in visitor's browsers.

<img width="1541" height="439" alt="decidim-html-xss-01" src="https://github.com/user-attachments/assets/acae1c06-8acb-49be-ab12-aabae33190ce" />

<img width="1540" height="752" alt="decidim-html-xss-02" src="https://github.com/user-attachments/assets/a2f1fa7f-03f3-4d17-b58b-f4db865443e9" />


### Impact

- A user with landing-page editing rights for an affected scope can persist JavaScript that executes in visitor's browsers on that page.
- Because exploitation already requires privileged administrative access, the practical risk is lower than a participant-controlled or unauthenticated stored XSS. It still creates a browser-execution primitive in a trusted admin-editable surface.

### Patches

See https://github.com/decidim/decidim/pull/16451 

### Workarounds

Do not give admin permissions to non-trustful users. 

### Reference

Stored XSS

### Credits

This issue was discovered in a security audit organized by the [Decidim Association](https://decidim.org) and made by [Radically Open Security](https://www.radicallyopensecurity.com/) against Decidim financed by [NGI](https://ngi.eu/).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-533c-2vh9-4r86
- https://github.com/decidim/decidim/pull/16451
- https://github.com/decidim/decidim
