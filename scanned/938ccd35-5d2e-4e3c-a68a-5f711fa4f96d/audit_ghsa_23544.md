# [H] Yelp OSXCollector Improper Certificate Validation

## Summary
Severity: High
Advisory: GHSA-g3cc-pvjj-9xq9
CVE: CVE-2018-10406
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-g3cc-pvjj-9xq9
Type: github-advisory

## Affected
- PyPI: `osxcollector` — affected >=0 <1.10

## Details
An issue was discovered in Yelp OSXCollector. A maliciously crafted Universal/fat binary can evade third-party code signing checks. By not completing full inspection of the Universal/fat binary, the user of the third-party tool will believe that the code is signed by Apple, but the malicious unsigned code will execute.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-10406
- https://github.com/Yelp/osxcollector/pull/160
- https://github.com/Yelp/osxcollector
- https://github.com/pypa/advisory-database/tree/main/vulns/osxcollector/PYSEC-2018-95.yaml
- https://thehackernews.com/2018/06/apple-mac-code-signing.html
- https://www.okta.com/security-blog/2018/06/issues-around-third-party-apple-code-signing-checks
