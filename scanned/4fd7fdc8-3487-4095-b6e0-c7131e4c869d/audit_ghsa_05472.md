# [M] Quick-Media Batik Codec FIX Package has Buffer Overflow Vulnerability in PNG Codec

## Summary
Severity: Medium
Advisory: GHSA-23f4-hfmq-94mj
CVE: CVE-2026-24807
CWE: CWE-120, CWE-190
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/S:N/AU:Y/R:U/V:C/RE:M/U:Amber (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-23f4-hfmq-94mj
Type: github-advisory

## Affected
- Maven: `com.github.liuyueyi.media:batik-codec-fix` — affected >=0

## Details
Improper Verification of Cryptographic Signature vulnerability in liuyueyi quick-media (plugins/svg-plugin/batik-codec-fix/src/main/java/org/apache/batik/ext/awt/image/codec/util modules). This vulnerability is associated with program files SeekableOutputStream.Java.

This issue affects all versions of quick-media. A patch is available: [3970e96](https://github.com/liuyueyi/quick-media/pull/123/commits/3970e967f6661328a5544fd0b977dac1a35e380b)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24807
- https://github.com/liuyueyi/quick-media/pull/123
- https://github.com/liuyueyi/quick-media/commit/3970e967f6661328a5544fd0b977dac1a35e380b
- https://github.com/liuyueyi/quick-media
