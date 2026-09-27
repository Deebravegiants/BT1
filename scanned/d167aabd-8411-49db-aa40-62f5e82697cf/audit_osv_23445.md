# [M] stakira OpenUtau ZIP Archive VoicebankInstaller.cs VoicebankInstaller path traversal

## Summary
Severity: Medium
Advisory: CVE-2022-4880
CVSS: 5.5 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-01-07
Source: https://osv.dev/vulnerability/CVE-2022-4880
Type: osv

## Details
A vulnerability was found in stakira OpenUtau. It has been classified as critical. This affects the function VoicebankInstaller of the file OpenUtau.Core/Classic/VoicebankInstaller.cs of the component ZIP Archive Handler. The manipulation leads to path traversal. Upgrading to version 0.0.991 is able to address this issue. The identifier of the patch is 849a0a6912aac8b1c28cc32aa1132a3140caff4a. It is recommended to upgrade the affected component. The identifier VDB-217617 was assigned to this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/4xxx/CVE-2022-4880.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-4880
- https://vuldb.com/?id.217617
- https://github.com/stakira/OpenUtau/pull/544
- https://vuldb.com/?ctiid.217617
- https://github.com/stakira/OpenUtau/commit/849a0a6912aac8b1c28cc32aa1132a3140caff4a
- https://github.com/stakira/OpenUtau/releases/tag/build%2F0.0.991
