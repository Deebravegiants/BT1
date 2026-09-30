# [M] SWC HTML minifier may allow script element breakout when minifying embedded JSON

## Summary
Severity: Medium
Advisory: CVE-2026-72925
Aliases: GHSA-5qr2-v392-m9g8
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-72925
Type: osv

## Details
SWC is a TypeScript / JavaScript compiler written in Rust. Prior to @swc/html 1.15.47-nightly-20260729.1 and swc_html_minifier 59.0.0, the minifyJson processing in crates/swc_html_minifier/src/lib.rs parsed and serialized attacker-controlled JSON in application/json and application/ld+json script elements without the escape_json_for_html_script behavior to re-escape less-than signs, allowing a closing script sequence to terminate the element early and execute script in the generated page's origin. This issue is fixed in @swc/html 1.15.47-nightly-20260729.1 and swc_html_minifier 59.0.0.

## References
- https://github.com/swc-project/swc/releases/tag/v1.15.47
- https://github.com/swc-project/swc/releases/tag/v1.15.47-nightly-20260729.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72925.json
- https://github.com/swc-project/swc/security/advisories/GHSA-5qr2-v392-m9g8
- https://nvd.nist.gov/vuln/detail/CVE-2026-72925
- https://github.com/swc-project/swc/commit/e1877b44bdac8abc9fd51e984d584f40f6999832
- https://github.com/swc-project/swc/pull/12080
