# [H] Imager versions from 0.45_02 before 1.034 for Perl may expose adjacent heap bytes via strlen() over-read from zero-count ASCII EXIF entries in copy_string_tags

## Summary
Severity: High
Advisory: CVE-2026-19082
Aliases: GHSA-hx46-55wp-hv6m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-19082
Type: osv

## Details
Imager versions from 0.45_02 before 1.034 for Perl may expose adjacent heap bytes via strlen() over-read from zero-count ASCII EXIF entries in copy_string_tags.

copy_string_tags() computes an ASCII EXIF tag's length as `entry->size - 1` to strip the trailing NUL. A zero-count ASCII entry sets `entry->size` to 0, and the derived length reaches i_tags_add() as -1, which is interpreted as a request to call strlen(), scanning past the entry to the next NUL and copying those bytes into the tag. JPEG reaches this path via im_decode_exif(), as does the separate Imager::File::WEBP distribution, which is fixed by upgrading Imager.

Any caller of Imager->read() on an attacker-supplied image with such an entry may receive an exif_* tag holding adjacent heap bytes instead of an empty string.

## References
- http://www.openwall.com/lists/oss-security/2026/08/07/6
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19082.json
- https://github.com/tonycoz/imager/security/advisories/GHSA-hx46-55wp-hv6m
- https://metacpan.org/release/TONYC/Imager-1.034/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-19082
- https://github.com/tonycoz/imager/commit/24bde0427a113264d53f45a9c29ae756d84c82fe.patch
- https://github.com/tonycoz/imager
