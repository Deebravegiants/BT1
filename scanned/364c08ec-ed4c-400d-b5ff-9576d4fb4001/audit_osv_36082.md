# [M] HTML::FormHandler versions before 0.410000 for Perl allow cross-site scripting via a submitted value rendered unescaped in an error message

## Summary
Severity: Medium
Advisory: CVE-2026-19872
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-09-08
Source: https://osv.dev/vulnerability/CVE-2026-19872
Type: osv

## Details
HTML::FormHandler versions before 0.410000 for Perl allow cross-site scripting via a submitted value rendered unescaped in an error message.

The wrappers and renderers that emit a form's errors interpolate the error string straight into HTML with no escaping. Two of the library's own messages, no_match and not_allowed, splice the submitted value into that string, and a failing type constraint puts the rejected value into the message it builds, which _apply_actions hands to add_error.

A field declared with a check regexp, a check list or a type constraint reaches those messages, with no custom validator and no non-default configuration. Errors rendered through an application's own escaping template layer rather than the library's rendering roles are not affected.

A request over the network that submits markup to such a field gets it back live inside the error span, running script in the victim's origin. Re-rendering a rejected value later gives the stored variant.

## References
- http://www.openwall.com/lists/oss-security/2026/09/08/15
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19872.json
- https://metacpan.org/release/ABRAXXA/HTML-FormHandler-0.410000/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-19872
- https://github.com/gshank/html-formhandler/commit/2574fdb4561f5c32d44cfbfbb3188345d49eb5a2.patch
- https://github.com/gshank/html-formhandler
