# [M] Open Redirect in xdLocalStorage

## Summary
Severity: Medium
Advisory: GHSA-c6c4-jmqx-3r33
CVE: CVE-2020-11611
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-c6c4-jmqx-3r33
Type: github-advisory

## Affected
- npm: `xdlocalstorage` — affected >=0

## Details
An issue was discovered in xdLocalStorage through 2.0.5. The buildMessage() function in xdLocalStorage.js specifies the wildcard (*) as the targetOrigin when calling the postMessage() function on the iframe object. Therefore any domain that is currently loaded within the iframe can receive the messages that the client sends.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11611
- https://github.com/ofirdagan/cross-domain-local-storage
- https://grimhacker.com/exploiting-xdlocalstorage-localstorage-and-postmessage/#Missing-TargetOrigin-Client
