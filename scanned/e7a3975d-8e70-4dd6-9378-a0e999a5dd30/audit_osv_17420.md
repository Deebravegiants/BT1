# [M] CVE-2020-15141

## Summary
Severity: Medium
Advisory: CVE-2020-15141
Aliases: GHSA-7wgr-7666-7pwj, PYSEC-2020-70
CVSS: 4.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:L/A:N)
Published: 2020-08-14
Source: https://osv.dev/vulnerability/CVE-2020-15141
Type: osv

## Details
In openapi-python-client before version 0.5.3, there is a path traversal vulnerability. If a user generated a client using a maliciously crafted OpenAPI document, it is possible for generated files to be placed in arbitrary locations on disk.

## References
- https://github.com/triaxtec/openapi-python-client/blob/main/CHANGELOG.md#053---2020-08-13
- https://github.com/triaxtec/openapi-python-client/security/advisories/GHSA-7wgr-7666-7pwj
- https://github.com/triaxtec/openapi-python-client/commit/3e7dfae5d0b3685abf1ede1bc6c086a116ac4746
- https://pypi.org/project/openapi-python-client
