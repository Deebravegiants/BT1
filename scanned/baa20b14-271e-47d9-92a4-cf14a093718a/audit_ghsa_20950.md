# [M] Improper beacon events in matrix-js-sdk can result in availability issues

## Summary
Severity: Medium
Advisory: GHSA-hvv8-5v86-r45x
CVE: CVE-2022-39236
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-09-29
Source: https://github.com/advisories/GHSA-hvv8-5v86-r45x
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=17.1.0-rc.1 <19.7.0

## Details
### Impact
Improperly formed beacon events (from [MSC3488](https://github.com/matrix-org/matrix-spec-proposals/pull/3488)) can disrupt or impede the matrix-js-sdk from functioning properly, potentially impacting the consumer's ability to process data safely. Note that the matrix-js-sdk can appear to be operating normally but be excluding or corrupting runtime data presented to the consumer.

### Patches
This is patched in matrix-js-sdk v19.7.0

### Workarounds
Redacting applicable events, waiting for the sync processor to store data, and restarting the client can often fix it. Alternatively, redacting the applicable events and clearing all storage will fix the further perceived issues.

Downgrading to an unaffected version, noting that such a version may be subject to other vulnerabilities, will additionally resolve the issue.

### References
N/A - This was a logic error in the SDK.

### For more information
If you have any questions or comments about this advisory please email us at [security at matrix.org](mailto:security@matrix.org).

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-hvv8-5v86-r45x
- https://nvd.nist.gov/vuln/detail/CVE-2022-39236
- https://github.com/matrix-org/matrix-spec-proposals/pull/3488
- https://github.com/matrix-org/matrix-js-sdk/commit/a587d7c36026fe1fcf93dfff63588abee359be76
- https://github.com/matrix-org/matrix-js-sdk
- https://github.com/matrix-org/matrix-js-sdk/releases/tag/v19.7.0
- https://security.gentoo.org/glsa/202210-35
