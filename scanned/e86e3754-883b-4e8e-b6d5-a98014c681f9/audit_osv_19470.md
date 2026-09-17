# [M] CVE-2021-21369

## Summary
Severity: Medium
Advisory: CVE-2021-21369
Aliases: GHSA-qgfj-mjpc-7w3q
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-09
Source: https://osv.dev/vulnerability/CVE-2021-21369
Type: osv

## Details
Hyperledger Besu is an open-source, MainNet compatible, Ethereum client written in Java. In Besu before version 1.5.1 there is a denial-of-service vulnerability involving the HTTP JSON-RPC API service. If username and password authentication is enabled for the HTTP JSON-RPC API service, then prior to making any requests to an API endpoint the requestor must use the login endpoint to obtain a JSON web token (JWT) using their credentials. A single user can readily overload the login endpoint with invalid requests (incorrect password). As the supplied password is checked for validity on the main vertx event loop and takes a relatively long time this can cause the processing of other valid requests to fail. A valid username is required for this vulnerability to be exposed. This has been fixed in version 1.5.1.

## References
- https://github.com/hyperledger/besu/blob/master/CHANGELOG.md#151
- https://github.com/hyperledger/besu/security/advisories/GHSA-qgfj-mjpc-7w3q
- https://github.com/hyperledger/besu/commit/06e35a58c07a30c0fbdc0aae45a3e8b06b53c022
- https://github.com/hyperledger/besu/pull/1144
