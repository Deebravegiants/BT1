# [M] Concrete CMS 9 through 9.5.2 is vulnerable to Server-Side Template Injection (SSTI) in Theme Customizer via Unvalidated Style Values

## Summary
Severity: Medium
Advisory: CVE-2026-81910
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-09-11
Source: https://osv.dev/vulnerability/CVE-2026-81910
Type: osv

## Details
Concrete CMS 9 through 9.5.2 is vulnerable to Server-Side Template Injection (SSTI) in Theme Customizer via Unvalidated Style Values. Values submitted through the customizer (color channels and other style properties handled by ColorStyle and sibling Style classes such as FontFamilyStyle and ImageStyle) are interpolated into server-compiled LESS source without neutralization of LESS syntax, allowing a user with the Theme Customization permission to inject arbitrary LESS directives. By injecting the @import (inline) directive, an attacker can read arbitrary files on the server and reach internal network resources through PHP stream wrappers. The compiled output, including any disclosed file contents, is written to the site's publicly served CSS cache, exposing database credentials, private keys, and other application secrets, and enabling server-side request forgery. The Concrete CMS security team gave this vulnerability a CVSS v4.0 score of 5.9 with vector CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N. Thanks Yonatan Drori from Tenzai for reporting.

## References
- https://documentation.concretecms.org/developers/introduction/version-history/953-release-notes
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81910.json
- https://github.com/concretecms/concretecms
- https://nvd.nist.gov/vuln/detail/CVE-2026-81910
