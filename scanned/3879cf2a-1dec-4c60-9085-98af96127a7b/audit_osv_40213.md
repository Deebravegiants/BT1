# [M] Template::Plugin::HTML versions through 3.102 for Perl allows HTML and JavaScript to be injected

## Summary
Severity: Medium
Advisory: CVE-2026-5090
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-05-19
Source: https://osv.dev/vulnerability/CVE-2026-5090
Type: osv

## Details
Template::Plugin::HTML versions through 3.102 for Perl allows HTML and JavaScript to be injected.

The html_filter function did not escape single quotes. HTML attributes inside of single quotes could be have code injected.  For example, the variable "var" in

    <a id='ref' title='[% var | html %]'>

would not be properly escaped. An attacker could insert some limited HTML and JavaScript, for example,

    var = " ' onclick='while (true) { alert(1) }'"

Note that arbitrary HTML and JavaScript would be difficult to inject, because angle brackets, ampersands and double-quotes would still be escaped.

## References
- http://www.openwall.com/lists/oss-security/2026/05/19/40
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5090.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-5090
- https://github.com/abw/Template2/issues/327
- https://github.com/abw/Template2/pull/337/changes/11c78a7a771d4af505efeb754a0b8775689c2eae
- https://github.com/abw/Template2
