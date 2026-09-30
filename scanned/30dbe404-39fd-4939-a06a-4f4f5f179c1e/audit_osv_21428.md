# [C] CVE-2021-4295

## Summary
Severity: Critical
Advisory: CVE-2021-4295
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-29
Source: https://osv.dev/vulnerability/CVE-2021-4295
Type: osv

## Details
A vulnerability classified as problematic was found in ONC code-validator-api up to 1.0.30. This vulnerability affects the function vocabularyValidationConfigurations of the file src/main/java/org/sitenv/vocabularies/configuration/CodeValidatorApiConfiguration.java of the component XML Handler. The manipulation leads to xml external entity reference. Upgrading to version 1.0.31 is able to address this issue. The name of the patch is fbd8ea121755a2d3d116b13f235bc8b61d8449af. It is recommended to upgrade the affected component. VDB-217018 is the identifier assigned to this vulnerability.

## References
- https://github.com/onc-healthit/code-validator-api/pull/97
- https://github.com/onc-healthit/code-validator-api/releases/tag/1.0.31
- https://vuldb.com/?ctiid.217018
- https://vuldb.com/?id.217018
- https://github.com/onc-healthit/code-validator-api/commit/fbd8ea121755a2d3d116b13f235bc8b61d8449af
