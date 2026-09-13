# [C] SCIFIO vulnerable to Path Traversal

## Summary
Severity: Critical
Advisory: GHSA-cmwm-45mj-mpg3
CVE: CVE-2022-4493
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-14
Source: https://github.com/advisories/GHSA-cmwm-45mj-mpg3
Type: github-advisory

## Affected
- Maven: `io.scif:scifio` — affected >=0 <0.43.3

## Details
A vulnerability classified as critical was found in scifio. Affected by this vulnerability is the function downloadAndUnpackResource of the file src/test/java/io/scif/util/DefaultSampleFilesService.java of the component ZIP File Handler. The manipulation leads to path traversal. The attack can be launched remotely. The patch is at commit fcb0dbca0ec72b22fe0c9ddc8abc9cb188a0ff31. It is recommended to apply a patch to fix this issue. The associated identifier of this vulnerability is VDB-215803.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4493
- https://github.com/scifio/scifio/commit/fcb0dbca0ec72b22fe0c9ddc8abc9cb188a0ff31
- https://github.com/scifio/scifio
- https://vuldb.com/?id.215803
