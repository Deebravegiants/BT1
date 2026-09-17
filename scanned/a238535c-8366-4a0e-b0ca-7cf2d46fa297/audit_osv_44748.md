# [M] Text::LineFold versions through 2019.001 for Perl duplicate the output based on the number of special break characters

## Summary
Severity: Medium
Advisory: CVE-2026-8594
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-30
Source: https://osv.dev/vulnerability/CVE-2026-8594
Type: osv

## Details
Text::LineFold versions through 2019.001 for Perl duplicate the output based on the number of special break characters.

Text::LineFold splits the input string by specific line break characters (such as VT, FF and others) into segments, but applies the break function to the entire string, not just the segment.

A side effect of this is that the full input can be duplicated for each segment.  Besides being incorrect, this can lead to unexpected resource consumption and possible denial of service.

Note that Text::LineFold is part of the Unicode-LineBreak distribution, which may have a higher version number than the module.

## References
- http://www.openwall.com/lists/oss-security/2026/05/30/6
- https://cpan.org/modules
- https://github.com/hatukanezumi/Unicode-LineBreak/
- https://metacpan.org/release/NEZUMI/Unicode-LineBreak-2019.001/source/lib/Text/LineFold.pm#L407-415
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/8xxx/CVE-2026-8594.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-8594
- https://github.com/hatukanezumi/Unicode-LineBreak/pull/6
- https://security.metacpan.org/patches/U/Unicode-LineBreak/2019.001/CVE-2026-8594-r1.patch
