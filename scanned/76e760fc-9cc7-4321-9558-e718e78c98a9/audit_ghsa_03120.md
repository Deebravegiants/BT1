# [H] Arbitrary code execution in ExifTool

## Summary
Severity: High
Advisory: GHSA-4whq-r978-2x68
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-04
Source: https://github.com/advisories/GHSA-4whq-r978-2x68
Type: github-advisory

## Affected
- npm: `exiftool-vendored` — affected >=0 <14.3.0

## Details
### Impact

Arbitrary code execution can occur when running `exiftool` against files with hostile metadata payloads.

### Patches

ExifTool has already been patched in version 12.24. exiftool-vendored, which vendors ExifTool, includes this patch in v14.3.0.

### Workarounds

No.

### References

https://twitter.com/wcbowling/status/1385803927321415687
https://nvd.nist.gov/vuln/detail/CVE-2021-22204

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [exiftool-vendored](https://github.com/photostructure/exiftool-vendored.js)

## References
- https://github.com/photostructure/exiftool-vendored.js/security/advisories/GHSA-4whq-r978-2x68
- https://github.com/photostructure/exiftool-vendored.js
