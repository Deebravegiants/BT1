# [M] Quadratic regex backtracking in the html_sanitize_ex CSS scrubber allows CPU-exhaustion denial of service

## Summary
Severity: Medium
Advisory: CVE-2026-68749
Aliases: EEF-CVE-2026-68749, GHSA-4cx2-987x-rr2x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-68749
Type: osv

## Details
Inefficient Regular Expression Complexity vulnerability in the CSS scrubber in rrrene html_sanitize_ex allows an unauthenticated remote attacker to exhaust server CPU via a long CSS declaration in sanitized HTML. The declaration regex in HtmlSanitizeEx.Scrubber.CSS.scrub/1 matches the property name with an unbounded greedy [-\w]+ followed by a mandatory :, so a long run of word characters not followed by a colon makes the engine give back one character at a time and retry the colon at every start offset. The work is quadratic in the length of the run, and no length cap is applied to the CSS handed to the scrubber. An 80 KB <style> body costs roughly 2.4 seconds of scheduler time, so a few concurrent requests saturate the BEAM scheduler pool and make the application unresponsive.

The impact is CPU exhaustion only. Nothing is read, modified or disclosed.

This issue affects html_sanitize_ex: from 0.3.1 before 1.4.5 and from 1.5.0-rc.0 before 1.5.3.

## References
- https://cna.erlef.org/cves/CVE-2026-68749.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-68749
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68749.json
- https://github.com/rrrene/html_sanitize_ex/security/advisories/GHSA-4cx2-987x-rr2x
- https://nvd.nist.gov/vuln/detail/CVE-2026-68749
- https://github.com/rrrene/html_sanitize_ex/commit/4f4bd9eb254881462c0461fbab74b29188c2c133
- https://github.com/rrrene/html_sanitize_ex/commit/b673df33ddf982c8bd0a8bd6348aa247080b3b14
- https://github.com/rrrene/html_sanitize_ex
