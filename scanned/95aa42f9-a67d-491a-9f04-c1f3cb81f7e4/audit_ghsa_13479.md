# [H] Bundled libwebp in imagecodecs vulnerable

## Summary
Severity: High
Advisory: GHSA-94vc-p8w7-5p49
Ecosystem: PyPI
Published: 2023-10-05
Source: https://github.com/advisories/GHSA-94vc-p8w7-5p49
Type: github-advisory

## Affected
- PyPI: `imagecodecs` — affected >=0 <2023.9.18

## Details
imagecodecs versions before v2023.9.18 bundled libwebp binaries in wheels that are vulnerable to CVE-2023-5129 (previously CVE-2023-4863). imagecodecs v2023.9.18 upgrades the bundled libwebp binary to v1.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4863
- https://nvd.nist.gov/vuln/detail/CVE-2023-5129
- https://github.com/cgohlke/imagecodecs
- https://github.com/cgohlke/imagecodecs/blob/v2023.9.18/CHANGES.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/imagecodecs/PYSEC-2023-174.yaml
