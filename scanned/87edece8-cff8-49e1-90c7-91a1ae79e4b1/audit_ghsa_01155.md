# [M] Invalid root may become trusted root in The Update Framework (TUF)

## Summary
Severity: Medium
Advisory: GHSA-f8mr-jv2c-v8mg
CVE: CVE-2020-15163
CWE: CWE-345, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-09-09
Source: https://github.com/advisories/GHSA-f8mr-jv2c-v8mg
Type: github-advisory

## Affected
- PyPI: `tuf` — affected >=0 <0.12.0

## Details
### Impact
The Python TUF reference implementation `tuf<0.12` will incorrectly trust a previously downloaded root metadata file which failed verification at download time. This allows an attacker who is able to serve multiple new versions of root metadata (i.e. by a man-in-the-middle attack) culminating in a version which has not been correctly signed to control the trust chain for future updates.

While investigating the reported vulnerability, we discovered that the detailed client workflow was not fully implemented. Specifically, for step 1.3 the newly downloaded root metadata was not being verified with a threshold of keys specified in the new root metadata file.
This missing step of the client workflow has been implemented in [PR #1101](https://github.com/theupdateframework/tuf/pull/1101), which is included in [v0.14.0](https://github.com/theupdateframework/tuf/releases/tag/v0.14.0) of tuf.

### Patches
A [fix](https://github.com/theupdateframework/tuf/pull/885), is available in version [0.12](https://github.com/theupdateframework/tuf/releases/tag/v0.12.0) and newer.

### Workarounds
No workarounds are known for this issue.

### References
* Pull request resolving the invalid root becoming trusted issue [PR 885](https://github.com/theupdateframework/tuf/pull/885)
* Pull request implementing self verification of newly downloaded root metadata [PR 1101](https://github.com/theupdateframework/tuf/pull/1101)

## References
- https://github.com/theupdateframework/tuf/security/advisories/GHSA-f8mr-jv2c-v8mg
- https://nvd.nist.gov/vuln/detail/CVE-2020-15163
- https://github.com/theupdateframework/tuf/pull/885
- https://github.com/theupdateframework/tuf/commit/3d342e648fbacdf43a13d7ba8886aaaf07334af7
- https://github.com/pypa/advisory-database/tree/main/vulns/tuf/PYSEC-2020-145.yaml
- https://github.com/theupdateframework/tuf
- https://github.com/theupdateframework/tuf/releases/tag/v0.12.0
- https://pypi.org/project/tuf
