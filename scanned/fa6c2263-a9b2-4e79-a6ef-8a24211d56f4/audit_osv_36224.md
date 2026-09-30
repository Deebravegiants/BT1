# [M] Panda3D <= 1.10.16 egg-mkfont Stack Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2026-22189
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-22189
Type: osv

## Details
The egg-mkfont utility in Panda3D versions up to and including 1.10.16 contains a stack-based buffer overflow vulnerability due to use of an unbounded sprintf() call with attacker-controlled input. When constructing glyph filenames, egg-mkfont formats a user-supplied glyph pattern (-gp) into a fixed-size stack buffer without length validation. Supplying an excessively long glyph pattern string can overflow the stack buffer, resulting in memory corruption and a deterministic crash. Depending on build configuration and execution environment, the overflow may also be exploitable for arbitrary code execution.

## References
- https://www.panda3d.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22189.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-22189
- https://www.vulncheck.com/advisories/panda3d-egg-mkfont-stack-buffer-overflow
- https://github.com/panda3d/panda3d
- https://seclists.org/fulldisclosure/2026/Jan/10
