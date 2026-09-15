# [H] IO::Compress versions from 2.207 before 2.220 for Perl ship a zipdetails CLI tool that crashes with undefined subroutine on Info-ZIP Unix Extra Field with 8-byte UID or GID

## Summary
Severity: High
Advisory: CVE-2026-48961
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-48961
Type: osv

## Details
IO::Compress versions from 2.207 before 2.220 for Perl ship a zipdetails CLI tool that crashes with undefined subroutine on Info-ZIP Unix Extra Field with 8-byte UID or GID.

When decode_ux() in bin/zipdetails handles an Info-ZIP Unix Extra Field (tag 0x7875) with UID Size or GID Size set to 8, causing zipdetails to decode an 8-byte UID or GID value, it dispatches through decodeLitteEndian(), which calls a misnamed helper unpackValueQ. The actual function defined in the same file is unpackValue_Q (with underscore); the call raises 'Undefined subroutine &main::unpackValueQ' and the script exits with status 255.

Library callers of IO::Compress and IO::Uncompress are not affected; the defect is in the bundled CLI tool.

## References
- http://www.openwall.com/lists/oss-security/2026/05/27/3
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48961.json
- https://metacpan.org/release/PMQS/IO-Compress-2.220/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-48961
- https://github.com/pmqs/IO-Compress/commit/33c89d03d6e746ed2ead4f2f6570d47864c61bc7.patch
- https://github.com/pmqs/IO-Compress
