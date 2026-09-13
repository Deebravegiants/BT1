# [M] Quadratic sibling re-flattening in the html_sanitize_ex traversal engine allows CPU-exhaustion denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-68750
Aliases: EEF-CVE-2026-68750, GHSA-463q-p2fr-mh9p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-68750
Type: osv

## Details
Inefficient Algorithmic Complexity vulnerability in the traversal engine in rrrene html_sanitize_ex allows an unauthenticated remote attacker to exhaust server CPU and memory via a flat run of sibling elements in sanitized HTML. The list clause of HtmlSanitizeEx.Traverser.traverse/2 recurses on the tail of a sibling list and then evaluates List.flatten([head] ++ tail) over the already flattened result, so every one of n siblings copies and re-walks the entire remaining tail. The flattening is only needed for the rare case where scrub returns several replacement nodes for one node, but the cost is paid across the whole tail at every step, making traversal quadratic in sibling count.

The traverser sits on every public entry point, so no particular scrubber or configuration is required and the payload needs only allowed tags. A 160 KB body of 20,000 sibling elements occupies a scheduler for roughly 1.7 seconds, and the cost grows faster than the body does.

This issue affects html_sanitize_ex: from 0.3.1 before 1.4.5 and from 1.5.0-rc.0 before 1.5.3.

## References
- https://cna.erlef.org/cves/CVE-2026-68750.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-68750
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68750.json
- https://github.com/rrrene/html_sanitize_ex/security/advisories/GHSA-463q-p2fr-mh9p
- https://nvd.nist.gov/vuln/detail/CVE-2026-68750
- https://github.com/rrrene/html_sanitize_ex/commit/507a6fb95dd4c466cac8a8355d8989043e9fbcc1
- https://github.com/rrrene/html_sanitize_ex/commit/9f5ccedbed230930813f992a1e6906fcf485981e
- https://github.com/rrrene/html_sanitize_ex
