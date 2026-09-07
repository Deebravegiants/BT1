# [C] Missing validation of JWT signature in `ManyDesigns/Portofino`

## Summary
Severity: Critical
Advisory: GHSA-6g3c-2mh5-7q6x
CVE: CVE-2021-29451
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-19
Source: https://github.com/advisories/GHSA-6g3c-2mh5-7q6x
Type: github-advisory

## Affected
- Maven: `com.manydesigns:portofino-dispatcher` — affected >=5.0.0 <5.2.1
- Maven: `com.manydesigns:portofino-core` — affected >=5.0.0 <5.2.1

## Details
### Impact
[Portofino](https://github.com/ManyDesigns/Portofino) is an open source web development framework. Portofino before version 5.2.1 did not properly verify the signature of JSON Web Tokens.
This allows forging a valid JWT.

### Patches
The issue will be patched in the upcoming 5.2.1 release.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/ManyDesigns/Portofino](https://github.com/ManyDesigns/Portofino)

## References
- https://github.com/ManyDesigns/Portofino/security/advisories/GHSA-6g3c-2mh5-7q6x
- https://nvd.nist.gov/vuln/detail/CVE-2021-29451
- https://github.com/ManyDesigns/Portofino/commit/8c754a0ad234555e813dcbf9e57d637f9f23d8fb
- https://mvnrepository.com/artifact/com.manydesigns/portofino
