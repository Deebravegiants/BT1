# [M] HTML::FormHandler versions before 0.410002 for Perl render field attributes into HTML without escaping using the process_attrs method

## Summary
Severity: Medium
Advisory: CVE-2026-85630
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-85630
Type: osv

## Details
HTML::FormHandler versions before 0.410002 for Perl render field attributes into HTML without escaping using the process_attrs method.

Any application with fields or field labels where some attributes are built from data rather than literals allows attacker-influenced text in an attribute value that can override the field attributes or embed JavaScript in rendered pages.

For example, the RadioGroup widget uses the process_attrs method via the render_option and wrap_radio methods.

## References
- http://www.openwall.com/lists/oss-security/2026/09/08/18
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85630.json
- https://metacpan.org/release/ABRAXXA/HTML-FormHandler-0.410002/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-85630
- https://github.com/gshank/html-formhandler/commit/a887271e91d755e6486a9f433ae932deb1d2c4a6.patch
- https://github.com/gshank/html-formhandler
