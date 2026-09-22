# [H] matrix-js-sdk Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-rfv9-x7hh-xc32
CVE: CVE-2022-36059
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-28
Source: https://github.com/advisories/GHSA-rfv9-x7hh-xc32
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=0 <19.4.0

## Details
### Impact
Events sent with special strings in key places can temporarily disrupt or impede the matrix-js-sdk from functioning properly, potentially impacting the consumer's ability to process data safely. Note that the matrix-js-sdk can appear to be operating normally but be excluding or corrupting runtime data presented to the consumer.

### Patches
This is fixed in matrix-js-sdk 19.4.0.

### Workarounds
Redacting applicable events, waiting for the sync processor to store data, and restarting the client can often fix it. Alternatively, redacting the applicable events and clearing all storage will often fix most perceived issues.

In some cases, no workarounds are possible.

### References
https://learn.snyk.io/lessons/prototype-pollution/javascript/

### For more information
If you have any questions or comments about this advisory please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-rfv9-x7hh-xc32
- https://nvd.nist.gov/vuln/detail/CVE-2022-36059
- https://github.com/matrix-org/matrix-js-sdk
- https://github.com/matrix-org/matrix-js-sdk/releases/tag/v19.4.0
