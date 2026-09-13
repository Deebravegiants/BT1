# [M] GNU patch is vulnerable to a denial of service (DoS) due to improper validation of hunk (single...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1261
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/JLSEC-2026-1261
Type: osv

## Affected
- Julia: `patch_jll` — affected unspecified

## Details
GNU patch is vulnerable to a denial of service (DoS) due to improper validation of hunk (single block of changes in diff) line offsets in unified-diff input. A specially crafted patch can specify an extremely large line number, causing the application to enter an effectively infinite processing loop while attempting to locate the requested position.
This results in excessive CPU consumption and prevents the process from completing.
An attacker can trigger this behavior by supplying a malicious patch file, causing the utility to become unresponsive and require manual termination.

This issue has been fixed in the commit faba04ef4f2b410257f76c1b9dc85e350929c4b9

## References
- https://cert.pl/en/posts/2026/07/CVE-2026-56288
- https://cgit.git.savannah.gnu.org/cgit/patch.git
- https://cgit.git.savannah.gnu.org/cgit/patch.git/
- https://cgit.git.savannah.gnu.org/cgit/patch.git/commit/?id=faba04ef4f2b410257f76c1b9dc85e350929c4b9
- https://github.com/advisories/GHSA-3m3r-f94v-4mf8
- https://nvd.nist.gov/vuln/detail/CVE-2026-56289
