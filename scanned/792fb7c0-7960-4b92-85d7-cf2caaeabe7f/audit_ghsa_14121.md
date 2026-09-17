# [M] html inputs of type password recorded in plaintext when converted to text inputs

## Summary
Severity: Medium
Advisory: GHSA-9qpj-qq2r-5mcc
CVE: CVE-2023-33187
CWE: CWE-319
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-9qpj-qq2r-5mcc
Type: github-advisory

## Affected
- npm: `highlight.run` — affected >=0 <6.0.0

## Details
### Impact
Highlight may record passwords on customer deployments when a password html input is switched to `type="text"` via a javascript "Show Password" button. This differs from the expected behavior which always obfuscates `type="password"` inputs. A customer may assume that switching to `type="text"` would also not record this input; hence, they would not add additional `highlight-mask` css-class obfuscation to this part of the DOM, resulting in unintentional recording of a password value when a `Show Password` button is used.

### Patches
`highlight.run@6.0.0` resolves the issue via https://github.com/rrweb-io/rrweb/pull/1184
This patch tracks changes to the `type` attribute of an input to ensure an input that used to be a `type="password"` continues to be obfuscated. 

### Workarounds
We have deployed a change to our data ingest to obfuscate passwords server side from older clients.
This means that upgrading to the latest version of highlight.run is not necessary but recommended to prevent potential network transfer of recorded password data to our backend.

### References
https://github.com/rrweb-io/rrweb/pull/1184

## References
- https://github.com/highlight/highlight/security/advisories/GHSA-9qpj-qq2r-5mcc
- https://nvd.nist.gov/vuln/detail/CVE-2023-33187
- https://github.com/rrweb-io/rrweb/pull/1184
- https://github.com/highlight/highlight
