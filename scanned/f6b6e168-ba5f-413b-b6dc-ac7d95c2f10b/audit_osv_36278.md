# [M] Rizin has a heap overflow on mach0_chained_fixups.c

## Summary
Severity: Medium
Advisory: CVE-2026-22780
Aliases: GHSA-f3v7-xhmj-9cjj
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-02-02
Source: https://osv.dev/vulnerability/CVE-2026-22780
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. Prior to 0.8.2, a heap overflow can be exploited when a malicious mach0 file, having bogus entries for the dyld chained segments, is parsed by rizin. This vulnerability is fixed in 0.8.2.

## References
- https://github.com/rizinorg/rizin/blob/6dd0dba9ff4dc706f549d0cdcd93856b49e59aa0/librz/bin/format/mach0/mach0_chained_fixups.c#L200
- https://github.com/rizinorg/rizin/releases/tag/v0.8.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22780.json
- https://github.com/rizinorg/rizin/security/advisories/GHSA-f3v7-xhmj-9cjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-22780
- https://github.com/rizinorg/rizin/issues/5768
- https://github.com/rizinorg/rizin/commit/41ea75d5b07d9b41b27ae80675cdda65f1b1c989
- https://github.com/rizinorg/rizin/pull/5770
