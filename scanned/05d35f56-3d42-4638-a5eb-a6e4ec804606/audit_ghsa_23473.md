# [H] xdlocalstorage does not verify request origin

## Summary
Severity: High
Advisory: GHSA-mr5m-2385-2vcp
CVE: CVE-2020-11610
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mr5m-2385-2vcp
Type: github-advisory

## Affected
- npm: `xdlocalstorage` — affected >=0

## Details
An issue was discovered in xdLocalStorage through 2.0.5. The `postData()` function in `xdLocalStoragePostMessageApi.js` specifies the wildcard (`*`) as the targetOrigin when calling the `postMessage()` function on the parent object. Therefore any domain can load the application hosting the "magical iframe" and receive the messages that the "magical iframe" sends.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11610
- https://github.com/ofirdagan/cross-domain-local-storage/issues/17
- https://github.com/ofirdagan/cross-domain-local-storage/pull/19
- https://github.com/ofirdagan/cross-domain-local-storage
- https://grimhacker.com/exploiting-xdlocalstorage-localstorage-and-postmessage/#Missing-TargetOrigin-Magic-iframe
