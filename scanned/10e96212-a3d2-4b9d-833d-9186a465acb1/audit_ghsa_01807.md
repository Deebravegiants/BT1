# [H] Improper Input Validation in xdLocalStorage

## Summary
Severity: High
Advisory: GHSA-vrc7-6g8w-jh56
CVE: CVE-2015-9544
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-vrc7-6g8w-jh56
Type: github-advisory

## Affected
- npm: `xdlocalstorage` — affected >=0

## Details
An issue was discovered in xdLocalStorage through 2.0.5. The receiveMessage() function in xdLocalStoragePostMessageApi.js does not implement any validation of the origin of web messages. Remote attackers who can entice a user to load a malicious site can exploit this issue to impact the confidentiality and integrity of data in the local storage of the vulnerable site via malicious web messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-9544
- https://github.com/ofirdagan/cross-domain-local-storage/issues/17
- https://github.com/ofirdagan/cross-domain-local-storage/pull/19
- https://github.com/ofirdagan/cross-domain-local-storage
- https://grimhacker.com/exploiting-xdlocalstorage-localstorage-and-postmessage/#Missing-Origin-Magic-iframe
