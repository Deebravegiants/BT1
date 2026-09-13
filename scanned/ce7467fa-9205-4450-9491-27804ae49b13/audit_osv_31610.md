# [C] HTML::Gumbo versions before 0.19 for Perl disclose heap memory via type confusion

## Summary
Severity: Critical
Advisory: CVE-2025-15646
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-01
Source: https://osv.dev/vulnerability/CVE-2025-15646
Type: osv

## Details
HTML::Gumbo versions before 0.19 for Perl disclose heap memory via type confusion.

Support for the <template> element was added to libgumbo 0.10.0 in 2015, but the walk_tree function in lib/HTML/Gumbo.xs was not updated to support it. The element was treated as a text-node, where strlen() over-reads the heap block that the pointer addresses.

Any caller that runs parse() with the default format => 'string', or with format => 'tree', on input containing a <template> element serializes the over-read bytes into the returned result, disclosing bounded heap contents. format => 'callback' reaches a croak on the unhandled node type and is unaffected.

## References
- http://www.openwall.com/lists/oss-security/2026/07/01/7
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15646.json
- https://metacpan.org/release/BPS/HTML-Gumbo-0.19/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-15646
- https://bugs.debian.org/1104789
- https://github.com/bestpractical/HTML-Gumbo/commit/15c0598909d4a64f47ef0a1abc5051f4e113c186.patch
- https://github.com/bestpractical/HTML-Gumbo
