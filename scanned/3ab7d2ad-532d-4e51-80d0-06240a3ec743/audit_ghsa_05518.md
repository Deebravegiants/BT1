# [M] Quick-Media Batik Codec FIX package has Code Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-8623-9fwr-4cxv
CVE: CVE-2026-24806
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/S:N/AU:Y/R:U/V:C/RE:M/U:Amber (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-8623-9fwr-4cxv
Type: github-advisory

## Affected
- Maven: `com.github.liuyueyi.media:batik-codec-fix` — affected >=0

## Details
Improper Control of Generation of Code ('Code Injection') vulnerability in liuyueyi quick-media (plugins/svg-plugin/batik-codec-fix/src/main/java/org/apache/batik/ext/awt/image/codec/png modules). This vulnerability is associated with program files PNGImageEncoder.Java.

This issue affects all quick-media versions. A patch is available: [e52fcee](https://github.com/liuyueyi/quick-media/commit/e52fceee32775a6be8ed1e394fbe94f4f8db036a)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-24806
- https://github.com/liuyueyi/quick-media/pull/122
- https://github.com/liuyueyi/quick-media/commit/29c078450ad2865c7ad196c658cacfab55b207ee
- https://github.com/liuyueyi/quick-media
