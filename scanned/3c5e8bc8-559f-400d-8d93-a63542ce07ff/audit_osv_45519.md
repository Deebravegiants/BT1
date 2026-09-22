# [M] GNU gzip contains a vulnerability in the gzexe utility related to insecure temporary file...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1264
Ecosystem: Julia
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1264
Type: osv

## Affected
- Julia: `Gzip_jll` — affected unspecified

## Details
GNU gzip contains a vulnerability in the gzexe utility related to insecure temporary file handling. When the mktemp utility is not available in the user’s PATH, gzexe falls back to constructing a temporary file path based solely on the process ID (PID). This predictable filename is created without exclusive access or existence checks.
A local attacker can pre‑create the predicted temporary file path as a symbolic link pointing to an arbitrary file writable by the victim. When gzexe runs, it follows the symlink and overwrites the target file, resulting in a time‑of‑check to time‑of‑use (TOCTOU) condition that allows arbitrary file overwrite.

This issue has been fixed in the commit 4e6f8b24ab823146ab8776f0b7fe486ab34d4269

## References
- https://cert.pl/en/posts/2026/04/CVE-2026-41991
- https://cert.pl/en/posts/2026/04/CVE-2026-41991/
- https://cgit.git.savannah.gnu.org/cgit/gzip.git/commit/?id=4e6f8b24ab823146ab8776f0b7fe486ab34d4269
- https://github.com/advisories/GHSA-67v8-88jf-4x6q
- https://nvd.nist.gov/vuln/detail/CVE-2026-41991
- https://www.gnu.org/software/gzip
- https://www.gnu.org/software/gzip/
