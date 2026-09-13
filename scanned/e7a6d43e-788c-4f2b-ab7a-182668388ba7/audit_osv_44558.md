# [H] js-yaml: maxTotalMergeKeys does not limit CPU use for empty merge sources

## Summary
Severity: High
Advisory: CVE-2026-84375
Aliases: GHSA-2883-xcg3-v3hh
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84375
Type: osv

## Details
js-yaml is a JavaScript YAML parser and dumper. From 3.0.0 until 3.15.2 and 4.3.2, maxTotalMergeKeys in lib/js-yaml/loader.js and lib/loader.js does not count empty mapping sources while processing the merge key <<. An attacker can alias a large sequence of empty mappings into many merge targets, causing O(N * K) processing while totalMergeKeys remains unchanged and the configured resource limit is never reached. A relatively small YAML document can therefore cause prolonged CPU consumption in applications that parse untrusted YAML, and merge processing is enabled by default on these release lines. This issue is fixed in versions 3.15.2 and 4.3.2.

## References
- https://github.com/nodeca/js-yaml/releases/tag/3.15.2
- https://github.com/nodeca/js-yaml/releases/tag/4.3.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84375.json
- https://github.com/nodeca/js-yaml/security/advisories/GHSA-2883-xcg3-v3hh
- https://nvd.nist.gov/vuln/detail/CVE-2026-84375
- https://github.com/nodeca/js-yaml/commit/3485bc06ff8a0251505f44a00414d90df2466639
- https://github.com/nodeca/js-yaml/commit/6a8e05f9a485188ed730ac81e81ae221352ef480
- https://github.com/nodeca/js-yaml/commit/d90b6612a5a84385bdcb556c44578eac76dc0f6b
- https://github.com/nodeca/js-yaml/pull/797
