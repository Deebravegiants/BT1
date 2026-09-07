# [M] TYPO3 Denial of Service in Online Media Asset Handling

## Summary
Severity: Medium
Advisory: GHSA-f3wf-q4fj-3gxf
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-f3wf-q4fj-3gxf
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.32
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.21
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.2

## Details
Online Media Asset Handling (*`.youtube` and *`.vimeo` files) in the TYPO3 backend is vulnerable to denial of service. Putting large files with according file extensions results in high consumption of system resources. This can lead to exceeding limits of the current PHP process which results in a dysfunctional backend component. A valid backend user account or write access on the server system (e.g. SFTP) is needed in order to exploit this vulnerability.

## References
- https://github.com/TYPO3/typo3/commit/054799caf53b28ff92e00aff957fab88c45a7509
- https://github.com/TYPO3/typo3/commit/16567366e2a25c0cbed7208c3be9eda962e28c9b
- https://github.com/TYPO3/typo3/commit/7a5155e0137d01db7e5723849f0493ad5b0c98ac
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-12-11-6.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-011
