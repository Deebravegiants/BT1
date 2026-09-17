# [M] PDF::WebKit versions through 1.2 for Perl allow OS command injection via a 2-arg open() of the output path in to_pdf and of stylesheet paths in _style_tag_for

## Summary
Severity: Medium
Advisory: CVE-2026-17431
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-17431
Type: osv

## Details
PDF::WebKit versions through 1.2 for Perl allow OS command injection via a 2-arg open() of the output path in to_pdf and of stylesheet paths in _style_tag_for.

to_pdf reads the generated PDF back from its path argument, and _style_tag_for reads each entry of the stylesheets list, by assigning the path to a local @ARGV and reading it with the diamond operator, which opens each @ARGV element with Perl's 2-arg open(). A value that begins or ends with a pipe ("| cmd", "cmd |") is run as a command rather than opened as a file, and one that begins with a redirect ("> path", ">> path") opens that path for write or append. to_file forwards its path argument to to_pdf and reaches the same read.

Any caller that forwards untrusted input as the output path or as a stylesheets entry can run a command under the process UID; with the "cmd |" form the command's output is returned in place of the PDF, and with the "> path" form the named file is truncated. Stylesheets may only be added to an HTML source, so a URL or file source exposes the output path alone.

## References
- http://www.openwall.com/lists/oss-security/2026/08/13/3
- https://cpan.org/modules
- https://wkhtmltopdf.org/status.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17431.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17431
- https://github.com/kingpong/perl-PDF-WebKit/issues/8
- https://security.metacpan.org/patches/P/PDF-WebKit/1.2/CVE-2026-17431-r1.patch
- https://github.com/kingpong/perl-PDF-WebKit
