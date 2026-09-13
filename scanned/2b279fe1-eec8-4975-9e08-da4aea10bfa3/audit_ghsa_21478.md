# [M] Use of unclaimed s3 bucket in tests and examples

## Summary
Severity: Medium
Advisory: GHSA-rc39-g977-687w
CVE: CVE-2022-36022
CWE: CWE-330, CWE-344
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-rc39-g977-687w
Type: github-advisory

## Affected
- Maven: `org.deeplearning4j:platform-tests` — affected >=0
- Maven: `org.deeplearning4j:dl4j-examples` — affected >=0

## Details
### Impact
People who use some older NLP examples that reference the old S3 bucket.

### Patches
The problem has been patched. Upgrade to snapshots for now. A release will be published later to address this due to the  vulnerability mostly being examples and 1 class in the actual code base.

### Workarounds
Download a word2vec google news vector from a new source using git lfs

## References
- https://github.com/deeplearning4j/deeplearning4j/security/advisories/GHSA-rc39-g977-687w
- https://github.com/eclipse/deeplearning4j/security/advisories/GHSA-rc39-g977-687w
- https://nvd.nist.gov/vuln/detail/CVE-2022-36022
- https://github.com/deeplearning4j/deeplearning4j
- https://github.com/mmihaltz/word2vec-GoogleNews-vectors
