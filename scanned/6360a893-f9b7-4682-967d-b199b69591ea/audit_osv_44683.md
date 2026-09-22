# [M] HTML::FormHandler versions before 0.410002 for Perl render option group labels and radio button labels into HTML without escaping

## Summary
Severity: Medium
Advisory: CVE-2026-85484
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-85484
Type: osv

## Details
HTML::FormHandler versions before 0.410002 for Perl render option group labels and radio button labels into HTML without escaping.

The Select, RadioGroup, CheckboxGroup and HorizCheckboxGroup widgets render a group label unescaped, Select into a label attribute and the other three into element content. RadioGroup also renders each radio button's own label unescaped.

Any application whose option list is built from data rather than literals, using options_from, an options_fieldname method, or the DBIC model, allows attacker-influenced text in a label that can override the options or embed JavaScript in rendered pages.

## References
- http://www.openwall.com/lists/oss-security/2026/09/08/16
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85484.json
- https://metacpan.org/release/ABRAXXA/HTML-FormHandler-0.410002/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-85484
- https://github.com/gshank/html-formhandler/commit/49b562e0fed5146fc1a372c5fa8a879876b8841d.patch
- https://github.com/gshank/html-formhandler
