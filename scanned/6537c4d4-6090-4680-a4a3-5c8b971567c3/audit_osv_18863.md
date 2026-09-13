# [C] CVE-2020-36628

## Summary
Severity: Critical
Advisory: CVE-2020-36628
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-25
Source: https://osv.dev/vulnerability/CVE-2020-36628
Type: osv

## Details
A vulnerability classified as critical has been found in Calsign APDE. This affects the function handleExtract of the file APDE/src/main/java/com/calsignlabs/apde/build/dag/CopyBuildTask.java of the component ZIP File Handler. The manipulation leads to path traversal. Upgrading to version 0.5.2-pre2-alpha is able to address this issue. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216747.

## References
- https://github.com/Calsign/APDE/releases/tag/v0.5.2-pre2-alpha
- https://vuldb.com/?id.216747
- https://github.com/Calsign/APDE/commit/c6d64cbe465348c1bfd211122d89e3117afadecf
