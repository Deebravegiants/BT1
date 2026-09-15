# [M] GNU patch is vulnerable to a NULL pointer dereference when processing a specially crafted unified...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1260
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1260
Type: osv

## Affected
- Julia: `patch_jll` — affected unspecified

## Details
GNU patch is vulnerable to a NULL pointer dereference when processing a specially crafted unified-diff patch file. Improper handling of consecutive end-of-file newline markers can corrupt internal hunk (single block of changes in diff) data structures, causing the application to pass a NULL pointer to fwrite() during patch processing.
An attacker can trigger this condition with a malicious patch file, causing the utility to crash and resulting in a denial of service.

This issue has been fixed in the commit e6d6a4e021660679d7fc9150f981d4920f722313

## References
- https://cert.pl/en/posts/2026/07/CVE-2026-56288
- https://cgit.git.savannah.gnu.org/cgit/patch.git
- https://cgit.git.savannah.gnu.org/cgit/patch.git/
- https://cgit.git.savannah.gnu.org/cgit/patch.git/commit/?id=e6d6a4e021660679d7fc9150f981d4920f722313
- https://github.com/advisories/GHSA-m3j2-9m66-r96h
- https://nvd.nist.gov/vuln/detail/CVE-2026-56288
