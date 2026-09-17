# [M] Improper file handling in matrix-react-sdk

## Summary
Severity: Medium
Advisory: GHSA-cg57-p69r-3m7p
CVE: CVE-2021-32622
CWE: CWE-434, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-cg57-p69r-3m7p
Type: github-advisory

## Affected
- npm: `matrix-react-sdk` — affected >=0 <3.21.0

## Details
Matrix-React-SDK is a react-based SDK for inserting a Matrix chat/voip client into a web page. Before version 3.21.0, when uploading a file, the local file preview can lead to execution of scripts embedded in the uploaded file. This can only occur after several user interactions to open the preview in a separate tab. This only impacts the local user while in the process of uploading. It cannot be exploited remotely or by other users. This vulnerability is patched in version 3.21.0.

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-8796-gc9j-63rv
- https://nvd.nist.gov/vuln/detail/CVE-2021-32622
- https://github.com/matrix-org/matrix-react-sdk/pull/5981
- https://www.npmjs.com/package/matrix-react-sdk
