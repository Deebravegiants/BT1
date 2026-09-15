# [M] Firebase JavaScript SDK allows attackers to manipulate the "_authTokenSyncURL" to point to their own server

## Summary
Severity: Medium
Advisory: GHSA-3wf4-68gx-mph8
CVE: CVE-2024-11023
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-3wf4-68gx-mph8
Type: github-advisory

## Affected
- npm: `firebase` — affected >=0 <10.9.0

## Details
Firebase JavaScript SDK utilizes a "FIREBASE_DEFAULTS" cookie to store configuration data, including an "_authTokenSyncURL" field used for session synchronization.  If this cookie field is preset via an attacker by any other method, the attacker can manipulate the "_authTokenSyncURL" to point to their own server and it would allow am actor to capture user session data transmitted by the SDK. We recommend upgrading Firebase JS SDK at least to 10.9.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-11023
- https://github.com/firebase/firebase-js-sdk/pull/8056
- https://github.com/firebase/firebase-js-sdk/commit/245dd26e19b6c16aca7e1b7e597ed5784c2984ba
- https://firebase.google.com/support/release-notes/js#version_1090_-_march_14_2024
- https://github.com/firebase/firebase-js-sdk
