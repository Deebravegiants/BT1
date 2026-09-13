# [M] CVE-2021-4437

## Summary
Severity: Medium
Advisory: CVE-2021-4437
Aliases: GHSA-m3f4-957x-m785
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-12
Source: https://osv.dev/vulnerability/CVE-2021-4437
Type: osv

## Details
A vulnerability, which was classified as problematic, has been found in dbartholomae lambda-middleware frameguard up to 1.0.4. Affected by this issue is some unknown functionality of the file packages/json-deserializer/src/JsonDeserializer.ts of the component JSON Mime-Type Handler. The manipulation leads to inefficient regular expression complexity. Upgrading to version 1.1.0 is able to address this issue. The patch is identified as f689404d830cbc1edd6a1018d3334ff5f44dc6a6. It is recommended to upgrade the affected component. VDB-253406 is the identifier assigned to this vulnerability.

## References
- https://github.com/dbartholomae/lambda-middleware/releases/tag/%40lambda-middleware%2Fframeguard_v1.1.0
- https://vuldb.com/?id.253406
- https://vuldb.com/?ctiid.253406
- https://github.com/dbartholomae/lambda-middleware/commit/f689404d830cbc1edd6a1018d3334ff5f44dc6a6
- https://github.com/dbartholomae/lambda-middleware/pull/57
