# [M] CVE-2021-21320

## Summary
Severity: Medium
Advisory: CVE-2021-21320
Aliases: GHSA-52mq-6jcv-j79x
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-03-02
Source: https://osv.dev/vulnerability/CVE-2021-21320
Type: osv

## Details
matrix-react-sdk is an npm package which is a Matrix SDK for React Javascript. In matrix-react-sdk before version 3.15.0, the user content sandbox can be abused to trick users into opening unexpected documents. The content is opened with a `blob` origin that cannot access Matrix user data, so messages and secrets are not at risk. This has been fixed in version 3.15.0.

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-52mq-6jcv-j79x
- https://www.npmjs.com/package/matrix-react-sdk
- https://github.com/matrix-org/matrix-react-sdk/commit/b386f0c73b95ecbb6ea7f8f79c6ff5171a8dedd1
- https://github.com/matrix-org/matrix-react-sdk/pull/5657
