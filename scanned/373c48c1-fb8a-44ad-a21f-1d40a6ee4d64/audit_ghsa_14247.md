# [M] matrix-js-sdk vulnerable to invisible eavesdropping in group calls

## Summary
Severity: Medium
Advisory: GHSA-6g67-q39g-r79q
CVE: CVE-2023-29529
CWE: CWE-862
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-04-14
Source: https://github.com/advisories/GHSA-6g67-q39g-r79q
Type: github-advisory

## Affected
- npm: `matrix-js-sdk` — affected >=0 <24.1.0

## Details
### Impact

An attacker present in a room where an [MSC3401](https://github.com/matrix-org/matrix-spec-proposals/pull/3401) group call is taking place can eavesdrop on the video and audio of participants using matrix-js-sdk, without their knowledge. To affected matrix-js-sdk users, the attacker will not appear to be participating in the call.

This attack is possible because matrix-js-sdk's group call implementation accepts incoming direct calls from other users, even if they have not yet declared intent to participate in the group call, as a means of resolving a race condition in call setup. Affected versions do not restrict access to the user's outbound media in this case.

Legacy 1:1 calls are unaffected.

### Workarounds

Users may hold group calls in private rooms where only the exact users who are expected to participate in the call are present.

## References
- https://github.com/matrix-org/matrix-js-sdk/security/advisories/GHSA-6g67-q39g-r79q
- https://nvd.nist.gov/vuln/detail/CVE-2023-29529
- https://github.com/matrix-org/matrix-spec-proposals/pull/3401
- https://github.com/matrix-org/matrix-js-sdk
- https://github.com/matrix-org/matrix-js-sdk/releases/tag/v24.1.0
