# [H] Apktool: Path Traversal to Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-m8mh-x359-vm8m
CVE: CVE-2026-39973
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-m8mh-x359-vm8m
Type: github-advisory

## Affected
- Maven: `org.apktool:apktool-lib` — affected >=3.0.0 <3.0.2

## Details
A path traversal vulnerability in `brut/androlib/res/decoder/ResFileDecoder.java` allows a maliciously crafted APK to write arbitrary files to the filesystem during standard decoding (`apktool d`). This is a security regression introduced in commit [e10a045](https://github.com/iBotPeaches/Apktool/commit/e10a0450c7afcd9462c0b76bcbff0e7428b92bdd#diff-cd531ebe1014bfd18185bf21585ca5cdb16fbcb07703ebc47949a1b4e4e36bc3) ([PR #4041](https://github.com/iBotPeaches/Apktool/pull/4041), December 12, 2025), which removed the `BrutIO.sanitizePath()` call that previously prevented path traversal in resource file output paths.

An attacker can embed `../` sequences in the `resources.arsc` Type String Pool to escape the output directory and write files to arbitrary locations, including `~/.ssh/config`, `~/.bashrc`, or Windows Startup folders, escalating to RCE.

**Fix:** Re-introduce `BrutIO.sanitizePath()` in `ResFileDecoder.java` before file write operations.

## References
- https://github.com/iBotPeaches/Apktool/security/advisories/GHSA-m8mh-x359-vm8m
- https://nvd.nist.gov/vuln/detail/CVE-2026-39973
- https://github.com/iBotPeaches/Apktool/pull/4041
- https://github.com/iBotPeaches/Apktool/commit/e10a0450c7afcd9462c0b76bcbff0e7428b92bdd#diff-cd531ebe1014bfd18185bf21585ca5cdb16fbcb07703ebc47949a1b4e4e36bc3
- https://github.com/iBotPeaches/Apktool
- https://github.com/iBotPeaches/Apktool/releases/tag/v3.0.2
