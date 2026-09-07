# [H] Fiona affected by CVE-2020-14152 related to madler-zlib

## Summary
Severity: High
Advisory: GHSA-g4m4-9q4c-mfw6
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2024-07-16
Source: https://github.com/advisories/GHSA-g4m4-9q4c-mfw6
Type: github-advisory

## Affected
- PyPI: `fiona` — affected >=0 <1.10b2

## Details
### Summary
Vulnerability scan of fiona shows [CVE-2020-14152](https://nvd.nist.gov/vuln/detail/CVE-2020-14152). The vulnerability is in libjpeg, a transitive dependency of fiona (via GDAL and PROJ).

### Details
In IJG JPEG (aka libjpeg) before 9d, jpeg_mem_available() in jmemnobs.c in djpeg does not honor the max_memory_to_use setting, possibly causing excessive memory consumption.

### Impact
fiona will not open JPEG files and is not vulnerable to attack in that way. fiona might be vulnerable to malformed PROJ grid files using JPEG compression. No such vulnerability or compromise has been demonstrated.

## References
- https://github.com/Toblerity/Fiona/security/advisories/GHSA-g4m4-9q4c-mfw6
- https://nvd.nist.gov/vuln/detail/CVE-2020-14152
- https://github.com/libjpeg-turbo/libjpeg-turbo/issues/500
- https://github.com/OSGeo/gdal/commit/075480a3cba13c9dd2ab4e39e92d6147a6c98eca
- https://github.com/Toblerity/Fiona/commit/07708211726e276e22dedb9cd567b4f6a7b8c809
- https://github.com/libjpeg-turbo/libjpeg-turbo/commit/da2a27ef056a0179cbd80f9146e58b89403d9933
- https://github.com/Toblerity/Fiona
