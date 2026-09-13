# [C] Code injection in BoofCV

## Summary
Severity: Critical
Advisory: GHSA-99p5-qpqx-mhwc
CVE: CVE-2023-39010
CWE: CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-99p5-qpqx-mhwc
Type: github-advisory

## Affected
- Maven: `org.boofcv:boofcv-core` — affected >=0 <0.43.1

## Details
BoofCV 0.42 was discovered to contain a code injection vulnerability via the component boofcv.io.calibration.CalibrationIO.load. This vulnerability is exploited by loading a crafted camera calibration file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-39010
- https://github.com/lessthanoptimal/BoofCV/issues/406
- https://github.com/lessthanoptimal/BoofCV/commit/0da6139ff69fd5a49359854ab01935d06c7f5aac
- https://github.com/lessthanoptimal/BoofCV
