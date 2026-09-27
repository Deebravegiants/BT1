# [H] CrateDB authentication bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-7mgx-gvjw-m3w3
CVE: CVE-2023-51982
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-30
Source: https://github.com/advisories/GHSA-7mgx-gvjw-m3w3
Type: github-advisory

## Affected
- Maven: `io.crate:crate` — affected >=0 <5.2.11
- Maven: `io.crate:crate` — affected >=5.3.0 <5.3.8
- Maven: `io.crate:crate` — affected >=5.4.0 <5.4.7
- Maven: `io.crate:crate` — affected >=5.5.0 <5.5.2

## Details
CrateDB 5.5.1 is contains an authentication bypass vulnerability in the Admin UI component. After configuring password authentication and_ Local_ In the case of an address, identity authentication can be bypassed by setting the X-Real IP request header to a specific value and accessing the Admin UI directly using the default user identity.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-51982
- https://github.com/crate/crate/issues/15231
- https://github.com/crate/crate/pull/15234
- https://github.com/crate/crate/commit/0c166ef083bec4d64dd55c1d8cb9b3dec350d241
- https://github.com/crate/crate/commit/5be7b3864137c23305ece10df3f7c311ee50ae4d
- https://github.com/crate/crate/commit/b8b4cec49a1c7eb2b5af568400bd571d194dc03e
- https://github.com/crate/crate/commit/da59311ca920743ebc58ee64c29cfe5723487f56
- https://github.com/crate/crate
- https://github.com/pypa/advisory-database/tree/main/vulns/crate/PYSEC-2024-27.yaml
