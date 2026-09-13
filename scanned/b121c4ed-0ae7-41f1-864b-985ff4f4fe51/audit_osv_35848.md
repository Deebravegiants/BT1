# [C] LOIDC nonce validation bypass

## Summary
Severity: Critical
Advisory: CVE-2026-15612
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-15612
Type: osv

## Details
Logto bypasses OIDC nonce validation when the nonce claim is absent from the id_token, enabling replay of authentication tokens and weakening session-binding.

## References
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/core/src/sso/OidcConnector/utils.ts#L175-L182
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15612.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15612
