# [H] SAML <Conditions> element not validated

## Summary
Severity: High
Advisory: CVE-2026-15615
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-15615
Type: osv

## Details
Logto omits validation of the SAML <Conditions> element, enabling attackers to strip time and audience restrictions and replay assertions indefinitely.

## References
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/connectors/connector-saml/src/utils.ts#L46-L110
- https://github.com/logto-io/logto/blob/ea3ede35028dfd0bbb6d7b239623ce0e7f6cdff8/packages/core/src/sso/SamlConnector/utils.ts#L175-L205
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15615.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15615
