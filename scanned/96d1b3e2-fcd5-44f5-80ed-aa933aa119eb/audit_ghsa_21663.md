# [H] Incorrect Authorization in NATS nats-server

## Summary
Severity: High
Advisory: GHSA-g6w6-r76c-28j7
CVE: CVE-2022-24450
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-08
Source: https://github.com/advisories/GHSA-g6w6-r76c-28j7
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.0.0 <2.7.2
- Go: `github.com/nats-io/nats-streaming-server` — affected >=0.15.0 <0.24.1

## Details
(This advisory is canonically <https://advisories.nats.io/CVE/CVE-2022-24450.txt>)

## Problem Description

NATS nats-server through 2022-02-04 has Incorrect Access Control, with unchecked ability for clients to authorize into any account, because of a coding error in a long-extant experimental feature.

A client crafting the initial protocol-level handshake could, with valid credentials for any account, specify a target account and switch into it immediately.  This includes any other tenant, and includes the System account which controls nats-server core operations.

For deployments not using multi-tenancy through NATS Accounts, there is still a vulnerability: normal users are able to choose to be in the System account.

An experimental feature to provide dynamically provisioned sandbox accounts was designed to allow a server administrator to turn on an option to allow clients to dynamically request a brand new account inline at connection time.  This feature went nowhere, but lived on in the code and was used by a number of tests; support was never added to any client libraries or to the documentation.

A bug in handling the feature meant that if someone did in fact have valid account credentials, then they could specify any other existing account and they would be assigned into that account.

Release 2.7.2 of nats-server removes the feature.
Because of the lack of client support and absence from protocol documentation, we feel this is safe operationally as well as the safest fix for the code.


## Affected versions

#### NATS Server
 * All 2.x versions up to and including 2.7.1.
 * Fixed with nats-io/nats-server: 2.7.2
 * NATS Server 1.x did not have accounts.
 * Docker image:  nats <https://hub.docker.com/_/nats>

#### NATS Streaming Server
 * All versions embedding affected NATS Server:
   + Affected: v0.15.0 up to and including v0.24.0
   + Fixed with nats-io/nats-streaming-server: 0.24.1
 * Docker image:  nats-streaming <https://hub.docker.com/_/nats-streaming>


## Impact

Existing users could act in any account, including the System account.

## Workaround

None.

## Solution

Upgrade the NATS server.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-g6w6-r76c-28j7
- https://nvd.nist.gov/vuln/detail/CVE-2022-24450
- https://advisories.nats.io/CVE/CVE-2022-24450.txt
- https://github.com/nats-io/nats-server
- https://github.com/nats-io/nats-server/releases/tag/v2.7.2
