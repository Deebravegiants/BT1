# [H] Imager::File::JPEG versions before 1.003 for Perl leak heap memory when reading a JPEG with repeated APP13 markers in i_readjpeg_wiol

## Summary
Severity: High
Advisory: CVE-2026-13708
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-13708
Type: osv

## Details
Imager::File::JPEG versions before 1.003 for Perl leak heap memory when reading a JPEG with repeated APP13 markers in i_readjpeg_wiol.

i_readjpeg_wiol walks the marker list libjpeg returns and, for each APP13 marker, allocates a new buffer with *iptc_itext = mymalloc(...) and overwrites the previous pointer without freeing it. Only the final payload is later turned into a Perl scalar and freed, so a JPEG with N such markers leaks the first N-1 payloads on every read.

In a long-lived process, such as an upload or thumbnailing service, repeated reads accumulate these leaks and exhaust available memory, a denial of service.

The same handler ships bundled in the Imager distribution, where versions before 1.032 are affected and the fix ships in 1.032.

## References
- http://www.openwall.com/lists/oss-security/2026/07/06/4
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13708.json
- https://metacpan.org/release/TONYC/Imager-File-JPEG-1.003/source/Changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-13708
- https://github.com/tonycoz/imager/commit/9f1c485ca3ee15dc261549e11afb356866552c3a.patch
- https://github.com/tonycoz/imager
