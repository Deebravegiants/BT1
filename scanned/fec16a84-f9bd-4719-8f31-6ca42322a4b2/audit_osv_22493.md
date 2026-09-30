# [C] Authentication bypass in Vartalap chat-server

## Summary
Severity: Critical
Advisory: CVE-2022-31013
Aliases: GHSA-xx4j-qqpp-v277
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2022-05-31
Source: https://osv.dev/vulnerability/CVE-2022-31013
Type: osv

## Details
Chat Server is the chat server for Vartalap, an open-source messaging application. Versions 2.3.2 until 2.6.0 suffer from a bug in validating the access token, resulting in authentication bypass. The function `this.authProvider.verifyAccessKey` is an async function, as the code is not using `await` to wait for the verification result. Every time the function responds back with success, along with an unhandled exception if the token is invalid. A patch is available in version 2.6.0.

## References
- https://github.com/ramank775/chat-server/discussions/78
- https://github.com/ramank775/chat-server/releases/tag/v2.6.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/31xxx/CVE-2022-31013.json
- https://github.com/ramank775/chat-server/security/advisories/GHSA-xx4j-qqpp-v277
- https://nvd.nist.gov/vuln/detail/CVE-2022-31013
