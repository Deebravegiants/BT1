# [M] Moodle Session Fixation allows unauthenticated users to hijack sessions via sesskey parameter

## Summary
Severity: Medium
Advisory: GHSA-cgvv-3455-824j
CVE: CVE-2025-53021
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-24
Source: https://github.com/advisories/GHSA-cgvv-3455-824j
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=3.0.0 <4.0.0

## Details
A session fixation vulnerability in Moodle 3.x through 3.11.18 allows unauthenticated attackers to hijack user sessions via the sesskey parameter. The sesskey can be obtained without authentication and reused within the OAuth2 login flow, resulting in the victim's session being linked to the attacker's. Successful exploitation results in full account takeover. According to the Moodle Releases page, "Bug fixes for security issues in 3.11.x ended 11 December 2023." NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53021
- https://github.com/moodle/moodle
- https://github.com/moodle/moodle/releases/tag/v3.11.18
- https://moodledev.io/general/releases#moodle-311
- https://rentry.co/moodle-oauth2-cve
