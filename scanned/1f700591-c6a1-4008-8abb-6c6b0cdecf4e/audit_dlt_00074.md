# [M] Denial of Service via Interrupted JSON-RPC Requests from Authenticated Clients

## Summary
Severity: Medium
Chain: Zcash
Component: ZcashFoundation/zebra
CWE: Uncaught Exception, Reachable Assertion
Published: 2026-04-17
Source: https://github.com/ZcashFoundation/zebra/security/advisories/GHSA-29x4-r6jv-ff4w
Type: github-advisory

## Details
A vulnerability in Zebra's JSON-RPC HTTP middleware allows an authenticated RPC client to cause a Zebra node to crash by disconnecting before the request body is fully received. The node treats the failure to read the HTTP request body as an unrecoverable error and aborts the process instead of returning an error response.

## Severity
**Moderate** - This is a Denial of Service (DoS) that requires a client capable of passing Zebra's cookie authentication, which is enabled by default.

## Affected Versions
- `zebrad`: versions from **2.2.0** up to (but not including) **4.3.1**
- `zebra-rpc`: versions from **1.0.0-beta.45** up to (but not including) **6.0.2**

## Description

Zebra's JSON-RPC HTTP middleware treated a failure to read the incoming HTTP request body as an unrecoverable error, aborting the process rather than returning an error response. A client that disconnected after sending only part of a request body, for example, by resetting the TCP connection mid-transfer, was sufficient to trigger the crash. The vulnerability could be exploited only by authenticated RPC clients. Nodes running the shipped defaults, with RPC bound to localhost and cookie authentication on, were not vulnerable.

## Impact
**Denial of Service**
* **Attack Vector:** Network, authenticated (requires a valid RPC cookie when cookie authentication is enabled).
* **Effect:** Immediate crash of the Zebra node.
* **Scope:** Any node whose RPC interface is reachable by a client with valid credentials, or any node with cookie authentication disabled and an exposed RPC interface.

## Fixed Versions
This issue is fixed in **Zebra 4.3.1** (crate `zebra-rpc` 6.0.2).

The fix propagates failures to read the HTTP request body as ordinary error responses, so Zebra now rejects truncated or interrupted requests rather than crashing.

## Mitigation
Users should upgrade to **Zebra 4.3.1** or later.

If an immediate upgrade is not possible, users should ensure their RPC port is not exposed to untrusted networks and that cookie authentication remains enabled (the default).

## References
* [Zebra 4.3.1 Release Announcement](https://zfnd.org/)

## Credits
Thanks to [shieldedonly](https://github.com/shieldedonly) who discovered this issue and reported it via our coordinated disclosure process.
