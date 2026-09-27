# [M] Capstone doesn't check vsnprintf return in SStream_concat, allows stack buffer underflow and overflow

## Summary
Severity: Medium
Advisory: CVE-2025-68114
Aliases: GHSA-85f5-6xr3-q76r
CVSS: 4.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2025-12-17
Source: https://osv.dev/vulnerability/CVE-2025-68114
Type: osv

## Details
Capstone is a disassembly framework. In versions 6.0.0-Alpha5 and prior, an unchecked vsnprintf return in SStream_concat lets a malicious cs_opt_mem.vsnprintf drive SStream’s index negative or past the end, leading to a stack buffer underflow/overflow when the next write occurs. Commit 2c7797182a1618be12017d7d41e0b6581d5d529e fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68114.json
- https://github.com/capstone-engine/capstone/security/advisories/GHSA-85f5-6xr3-q76r
- https://nvd.nist.gov/vuln/detail/CVE-2025-68114
- https://github.com/capstone-engine/capstone/commit/2c7797182a1618be12017d7d41e0b6581d5d529e
