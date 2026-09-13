# [C] PDF::WebKit versions through 1.2 for Perl allow argument injection into wkhtmltopdf via meta tags in the source document

## Summary
Severity: Critical
Advisory: CVE-2026-16770
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-16770
Type: osv

## Details
PDF::WebKit versions through 1.2 for Perl allow argument injection into wkhtmltopdf via meta tags in the source document.

For an HTML string or file source, the constructor collects every <meta name="pdf-webkit-KEY" content="VALUE"> element in the document head through _pdf_webkit_meta_tags and turns each one into a wkhtmltopdf command line option. KEY is normalized to an option name matching --[a-z0-9-]+ but is not checked against an allow list, VALUE is passed through unchanged as the argument that follows it, and a VALUE of "yes" emits the option as a bare flag. BUILD merges the meta derived options last, so they also override the module defaults and the options passed to new. Switches such as --enable-local-file-access and --cookie-jar are reachable this way. The renderer is executed with an argument list rather than a shell command, so this is argument injection and not shell injection.

Any caller that renders untrusted HTML lets the document choose the renderer's options and override those set by the application, including options that read local files into the resulting PDF or write to a chosen path. A URL source is not scanned, and the scan is skipped when XML::LibXML, a recommended dependency, is not installed.

## References
- http://www.openwall.com/lists/oss-security/2026/08/13/2
- https://cpan.org/modules
- https://wkhtmltopdf.org/status.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16770.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-16770
- https://github.com/kingpong/perl-PDF-WebKit/issues/9
- https://security.metacpan.org/patches/P/PDF-WebKit/1.2/CVE-2026-16770-r1.patch
- https://github.com/kingpong/perl-PDF-WebKit
