# [H] H2O Vulnerable to Arbitrary File Overwrite

## Summary
Severity: High
Advisory: GHSA-g48v-3p35-88jr
CVE: CVE-2024-8616
CWE: CWE-73
Ecosystem: Maven, PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-g48v-3p35-88jr
Type: github-advisory

## Affected
- PyPI: `h2o` — affected >=3.10.4.1
- Maven: `ai.h2o:h2o-core` — affected >=3.10.4.1

## Details
In h2oai/h2o-3 version 3.46.0, the `/99/Models/{name}/json` endpoint allows for arbitrary file overwrite on the target server. The vulnerability arises from the `exportModelDetails` function in `ModelsHandler.java`, where the user-controllable `mexport.dir` parameter is used to specify the file path for writing model details. This can lead to overwriting files at arbitrary locations on the host system.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8616
- https://github.com/h2oai/h2o-3
- https://github.com/h2oai/h2o-3/blob/088190f9d0370a02a483fca68d8dc89c996b4f83/h2o-core/src/main/java/water/api/ModelsHandler.java#L310
- https://huntr.com/bounties/aebf69a5-b9b1-4d2f-a8ff-902c11a8c97a
