# [H] OpenC3 Path Traversal via screen controller (`GHSL-2024-127`)

## Summary
Severity: High
Advisory: GHSA-8jxr-mccc-mwg8
CVE: CVE-2024-46977
CWE: CWE-22
Ecosystem: PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-8jxr-mccc-mwg8
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=0 <5.19.0
- PyPI: `openc3` — affected >=0 <5.19.0

## Details
### Summary
A path traversal vulnerability inside of `LocalMode`'s `open_local_file` method allows an authenticated user with adequate permissions to download any `.txt` via the `ScreensController#show` on the web server COSMOS is running on (depending on the file permissions).

Note: This CVE affects all OpenC3 COSMOS Editions

### Impact
This issue may lead to Information Disclosure.

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-8jxr-mccc-mwg8
- https://nvd.nist.gov/vuln/detail/CVE-2024-46977
- https://github.com/OpenC3/cosmos/commit/a34e61aea5a465f0ab3e57d833ae7ff4cafd710b
- https://github.com/OpenC3/cosmos
- https://github.com/pypa/advisory-database/tree/main/vulns/openc3/PYSEC-2024-101.yaml
- https://rubysec.com/advisories/CVE-2024-46977
- https://securitylab.github.com/advisories/GHSL-2024-127_GHSL-2024-129_OpenC3_COSMOS
