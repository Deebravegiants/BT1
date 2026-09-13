# [C] Potential buffer overflow in psd-tools

## Summary
Severity: Critical
Advisory: GHSA-22jr-vc7j-g762
CVE: CVE-2020-10571
CWE: CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-03-16
Source: https://github.com/advisories/GHSA-22jr-vc7j-g762
Type: github-advisory

## Affected
- PyPI: `psd-tools` — affected >=1.8.37 <1.9.4

## Details
### Impact
An issue was discovered in psd-tools before 1.9.4. The Cython implementation of RLE decoding did not check for malformed PSD input data during decoding to the PIL.Image or NumPy format, leading to a Buffer Overflow.

### Patches
Users of psd-tools version v1.8.37 to v1.9.3 should upgrade to v1.9.4.

### Workarounds
Without Cython present on installation, buffer overflow does not occur but IndexError will be thrown. However, already installed psd-tools with Cython extention should be upgraded.

### References
https://github.com/psd-tools/psd-tools/pull/198

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [psd-tools](https://github.com/psd-tools/psd-tools/issues)

## References
- https://github.com/psd-tools/psd-tools/security/advisories/GHSA-22jr-vc7j-g762
- https://nvd.nist.gov/vuln/detail/CVE-2020-10571
- https://github.com/psd-tools/psd-tools/pull/198
- https://github.com/psd-tools/psd-tools/commit/fd51f8b4a52bc9c1c06d1035dfdf2cd920e87074
- https://github.com/psd-tools/psd-tools
- https://github.com/psd-tools/psd-tools/releases/tag/v1.9.4
- https://github.com/pypa/advisory-database/tree/main/vulns/psd-tools/PYSEC-2020-91.yaml
