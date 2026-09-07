# [M] Mediawiki Cargo extension vulnerable to Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-jqvm-9xm2-gc38
CVE: CVE-2024-47847
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-10-05
Source: https://github.com/advisories/GHSA-jqvm-9xm2-gc38
Type: github-advisory

## Affected
- Packagist: `mediawiki/cargo` — affected >=0 <3.6.1

## Details
Improper Neutralization of Input During Web Page Generation (XSS or 'Cross-site Scripting') vulnerability in The Wikimedia Foundation Mediawiki - Cargo allows Cross-Site Scripting (XSS).This issue affects Mediawiki - Cargo: from 3.6.X before 3.6.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47847
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/Cargo/+/1063804
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/Cargo/+/1063806
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/Cargo/+/1063827
- https://gerrit.wikimedia.org/r/c/mediawiki/extensions/Cargo/+/1063831
- https://github.com/wikimedia/mediawiki-extensions-Cargo
- https://phabricator.wikimedia.org/T368628
- https://phabricator.wikimedia.org/T372211
