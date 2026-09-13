# [M] CVE-2024-55566

## Summary
Severity: Medium
Advisory: CVE-2024-55566
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/CVE-2024-55566
Type: osv

## Details
ColPack 1.0.10 through 9a7293a has a predictable temporary file (located under /tmp with a name derived from an unseeded RNG). The impact can be overwriting files or making ColPack graphing unavailable to other users.

## References
- https://cwe.mitre.org/data/definitions/335.html
- https://github.com/CSCsw/ColPack/blob/9a7293a8dfd66a60434496b8df5ebb4274d70339/src/Utilities/extra.cpp#L184-L190
- https://bugzilla.suse.com/show_bug.cgi?id=1225617
