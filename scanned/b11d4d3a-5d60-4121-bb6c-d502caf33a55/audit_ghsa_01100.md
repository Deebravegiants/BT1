# [H] Regular Expression Denial of Service in papaparse

## Summary
Severity: High
Advisory: GHSA-qvjc-g5vr-mfgr
CVE: CVE-2020-36649
CWE: CWE-185
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-qvjc-g5vr-mfgr
Type: github-advisory

## Affected
- npm: `papaparse` — affected >=0 <5.2.0

## Details
Versions of `papaparse` prior to 5.2.0 are vulnerable to Regular Expression Denial of Service (ReDos). The `parse` function contains a malformed regular expression that takes exponentially longer to process non-numerical inputs. This allows attackers to stall systems and lead to Denial of Service.


## Recommendation

Upgrade to version 5.2.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36649
- https://github.com/mholt/PapaParse/issues/777
- https://github.com/mholt/PapaParse/pull/779
- https://github.com/mholt/PapaParse/commit/235a12758cd77266d2e98fd715f53536b34ad621
- https://github.com/mholt/PapaParse
- https://github.com/mholt/PapaParse/releases/tag/5.2.0
- https://snyk.io/vuln/SNYK-JS-PAPAPARSE-564258
- https://vuldb.com/?ctiid.218004
- https://vuldb.com/?id.218004
