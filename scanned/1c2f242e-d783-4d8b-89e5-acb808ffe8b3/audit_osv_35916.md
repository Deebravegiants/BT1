# [C] Catalyst::View::Wkhtmltopdf versions before 0.6.1 for Perl allow shell command injection (RCE) via PDF render options

## Summary
Severity: Critical
Advisory: CVE-2026-16766
Aliases: GHSA-42w4-jj8w-6p98
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-16766
Type: osv

## Details
Catalyst::View::Wkhtmltopdf versions before 0.6.1 for Perl allow shell command injection (RCE) via PDF render options.

Options are passed directly to the wkhtmltopdf command without sanitization.

Any web application that passes user-controlled options such as the page_size, orientation or margins without validation allows shell command injection.

Version 0.6.0 was released with an incomplete fix for this issue.

Note that the wkhtmltopdf project is no longer being developed, and users of this package should migrate to alternative solutions.

## References
- http://www.openwall.com/lists/oss-security/2026/07/25/4
- https://cpan.org/modules
- https://wkhtmltopdf.org/status.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16766.json
- https://github.com/robrwo/Catalyst-View-Wkhtmltopdf/security/advisories/GHSA-42w4-jj8w-6p98
- https://metacpan.org/release/RRWO/Catalyst-View-Wkhtmltopdf-v0.6.1/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-16766
- https://github.com/mc7244/Catalyst-View-Wkhtmltopdf/issues/6
- https://github.com/robrwo/Catalyst-View-Wkhtmltopdf
