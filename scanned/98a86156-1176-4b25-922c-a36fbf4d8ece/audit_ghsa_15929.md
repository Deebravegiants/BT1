# [H] Malicious homeservers can steal message keys when the matrix-react-sdk user invites another user to a room

## Summary
Severity: High
Advisory: GHSA-qcvh-p9jq-wp8v
CVE: CVE-2024-47824
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N (CVSS_V3)
Published: 2024-10-15
Source: https://github.com/advisories/GHSA-qcvh-p9jq-wp8v
Type: github-advisory

## Affected
- npm: `matrix-react-sdk` — affected >=3.18.0 <3.102.0

## Details
### Impact

matrix-react-sdk before 3.102.0 allows a malicious homeserver to potentially steal message keys for a room when a user invites another user to that room, via injection of a malicious device controlled by the homeserver. This is possible because matrix-react-sdk before 3.102.0 shared historical message keys on invite.

### Patches

matrix-react-sdk 3.102.0 [disables sharing message keys on invite](https://github.com/matrix-org/matrix-react-sdk/pull/12618) by removing calls to the vulnerable functionality.

### Workarounds

None.

### References

The vulnerability in matrix-react-sdk is caused by calling `MatrixClient.sendSharedHistoryKeys` in matrix-js-sdk, which is inherently vulnerable to this sort of attack. This matrix-js-sdk vulnerability is tracked as CVE-2024-47080 / [GHSA-4jf8-g8wp-cx7c](https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-4jf8-g8wp-cx7c). Given that this functionality is not specific to sharing message keys on *invite*, is optional, has to be explicitly called by the caller and has been independently patched in matrix-react-sdk by removing the offending calls, we believe it is proper to treat the matrix-react-sdk vulnerability as a separate one, with its own advisory and CVE.

The matrix-org/matrix-react-sdk repository has recently been archived and the project was moved to [element-hq/matrix-react-sdk](https://github.com/element-hq/matrix-react-sdk). Given that this happened *after* the first patched release, no releases of the project on [element-hq/matrix-react-sdk](https://github.com/element-hq/matrix-react-sdk) were ever vulnerable to this vulnerability.

Patching pull request: https://github.com/matrix-org/matrix-react-sdk/pull/12618.

### For more information

If you have any questions or comments about this advisory, please email us at security at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-qcvh-p9jq-wp8v
- https://nvd.nist.gov/vuln/detail/CVE-2024-47824
- https://github.com/matrix-org/matrix-react-sdk/pull/12618
- https://github.com/matrix-org/matrix-react-sdk/commit/6fc9d7641c51ca3db8225cf58b9d6e6fdd2d6556
- https://github.com/matrix-org/matrix-react-sdk
