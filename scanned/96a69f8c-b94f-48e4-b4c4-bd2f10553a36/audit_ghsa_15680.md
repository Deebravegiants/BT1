# [C] Fiona affected by CVE-2023-45853 related to MiniZip madler-zlib

## Summary
Severity: Critical
Advisory: GHSA-q5fm-55c2-v6j9
CWE: CWE-1395, CWE-190
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-16
Source: https://github.com/advisories/GHSA-q5fm-55c2-v6j9
Type: github-advisory

## Affected
- PyPI: `fiona` — affected >=0 <1.10b1

## Details
### Summary
Vulnerability scan of fiona shows [CVE-2023-45853](https://nvd.nist.gov/vuln/detail/CVE-2023-45853). The vulnerability is in GDAL, a dependency of fiona.

### Details
Fiona depends on GDAL and GDAL has a port of minizip. MiniZip in zlib through 1.3 has an integer overflow and resultant heap-based buffer overflow in zipOpenNewFileInZip4_64 via a long filename, comment, or extra field. The GDAL project has addressed the CVE in version 3.8.0. See https://lists.osgeo.org/pipermail/gdal-dev/2023-November/057881.html.

The Fiona version 1.9.6 wheels on PyPI include GDAL version 3.6.4 and thus could be vulnerable. All of the Fiona 1.10 pre-release wheels in PyPI include GDAL version 3.8.4 and are not vulnerable.

### Impact
Systems which use GDAL versions prior to 3.8.0 to open unchecked zip files, whether in combination with fiona or not, could be susceptible to buffer overflows.

## References
- https://github.com/Toblerity/Fiona/security/advisories/GHSA-q5fm-55c2-v6j9
- https://nvd.nist.gov/vuln/detail/CVE-2023-45853
- https://github.com/OSGeo/gdal/commit/4aa7ca61c1d2191baf1eea2a97d0dec33a41691f
- https://github.com/madler/zlib/commit/73331a6a0481067628f065ffe87bb1d8f787d10c
- https://github.com/Toblerity/Fiona
