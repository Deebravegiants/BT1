# [H] strawberry-graphql: Authentication bypass via legacy graphql-ws WebSocket subprotocol

## Summary
Severity: High
Advisory: GHSA-vpwc-v33q-mq89
CVE: CVE-2026-35523
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-vpwc-v33q-mq89
Type: github-advisory

## Affected
- PyPI: `strawberry-graphql` — affected >=0 <0.312.3

## Details
Strawberry up until version `0.312.3` is vulnerable to an authentication bypass on WebSocket subscription endpoints. The legacy graphql-ws subprotocol handler does not verify that a `connection_init` handshake has been completed before processing start (subscription) messages. This allows a remote attacker to skip the `on_ws_connect` authentication hook entirely by connecting with the graphql-ws subprotocol and sending a start message directly, without ever sending `connection_init`.

The graphql-transport-ws subprotocol handler is not affected, as it correctly gates subscription operations on a connection_acknowledged flag. However, both subprotocols are enabled by default in all framework integrations that support websockets, and the subprotocol is selected by the client via the Sec-WebSocket-Protocol header.

Any application relying on `on_ws_connect` for authentication or authorization is affected.

Mitigation: Upgrade to the patched version, or explicitly disable the legacy graphql-ws subprotocol by setting `subscription_protocols=[GRAPHQL_TRANSPORT_WS_PROTOCOL]` on your GraphQL view/router.

## References
- https://github.com/strawberry-graphql/strawberry/security/advisories/GHSA-vpwc-v33q-mq89
- https://nvd.nist.gov/vuln/detail/CVE-2026-35523
- https://github.com/strawberry-graphql/strawberry/commit/0977a4e6b41b7cfe3e9d8ba84a43458a2b0c54c2
- https://github.com/pypa/advisory-database/tree/main/vulns/strawberry-graphql/PYSEC-2026-133.yaml
- https://github.com/strawberry-graphql/strawberry
- https://github.com/strawberry-graphql/strawberry/releases/tag/0.312.3
