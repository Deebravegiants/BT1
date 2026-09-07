# [M] Silverstripe Forum Module CSRF Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w8fq-xgvh-cxc2
CWE: CWE-352, CWE-425
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-w8fq-xgvh-cxc2
Type: github-advisory

## Affected
- Packagist: `silverstripe/forum` — affected >=0 <0.6.2
- Packagist: `silverstripe/forum` — affected >=0.7.0 <0.7.4

## Details
A number of form actions in the Forum module are directly accessible. A malicious user (e.g. spammer) can use GET requests to create Members and post to forums, bypassing CSRF and anti-spam measures.

Additionally, a forum moderator could be tricked into clicking a specially crafted URL, resulting in a topic being moved.

Thanks to Michael Strong for discovering.

## References
- https://github.com/silverstripe-archive/silverstripe-forum/commit/0ec7c92785f36c8edf4a11c36a4fc27e0c40cee6
- https://github.com/silverstripe-archive/silverstripe-forum/commit/efe09f95ccdb0138ce5bd3d3a21b3d9e97038dd8
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/forum/SS-2015-017-1.yaml
- https://github.com/silverstripe-archive/silverstripe-forum
- https://www.silverstripe.org/software/download/security-releases/ss-2015-017
