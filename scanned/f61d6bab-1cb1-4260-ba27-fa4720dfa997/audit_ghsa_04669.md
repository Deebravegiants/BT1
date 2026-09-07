# [H] Hysteria has an authenticated UDP ACL bypass that enables localhost and private-network UDP SSRF

## Summary
Severity: High
Advisory: GHSA-vgrc-hq28-p3xp
CWE: CWE-284, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-vgrc-hq28-p3xp
Type: github-advisory

## Affected
- Go: `github.com/apernet/hysteria/core/v2` — affected >=2.0.0 <2.9.2

## Details
## Summary

Hysteria's UDP relay treats the destination address as packet-scoped, but ACL and outbound policy are applied only once when a new UDP session is created. After an authenticated client opens a UDP session using an allowed first destination, later packets in the same `Session ID` can be sent to different destinations without re-running ACL evaluation.

This allows an authenticated user to bypass server-side UDP ACL rules and reach localhost or RFC1918/private-network UDP services from the server's network perspective, even when those destinations are explicitly rejected by ACL.

Verified on current HEAD at commit `64c396385631579598cc29d5561bff98c439772f`.

## Why this is a security issue

This report is not based on the assumption that one UDP session must be bound to one destination. The protocol and official client both support per-packet destinations:

- `PROTOCOL.md:93-107` defines each `UDPMessage` as carrying its own `Addr` field.
- `core/client/udp.go:52-62` exposes `Send(data, addr)`, allowing the same UDP session to send to arbitrary addresses.

The problem is that the security-relevant destination is packet-scoped, while ACL and outbound authorization are cached at session scope.

This is also not a `RequestHook`-bypass claim. I understand `RequestHook` is first-packet-oriented. The broader issue is that operator-configured ACL policy intended to block UDP destinations is not enforced on later packets within the same session.

Because the ACL documentation is presented as the mechanism for handling or blocking client requests, and includes examples of denying `udp/443` and private network CIDRs, operators can reasonably rely on ACL as a UDP egress security boundary. This boundary can currently be bypassed by reusing a previously authorized UDP session.

## Root cause

The relevant flow appears to be:

- `core/server/udp.go:280-299`: when a new session is created, the first destination is passed through `m.io.Hook(...)`, logged, and then `m.io.UDP(addr)` is called once to create the outbound UDP connection.
- `core/server/server.go:397-398`: `m.io.UDP(addr)` delegates to `io.Outbound.UDP(reqAddr)`.
- `app/cmd/server.go:1187-1190`: resolver, ACL, and actual outbounds are intentionally chained through the `Outbound` interface.
- `core/server/udp.go:125`: the initial outbound connection is created only from the first packet via `DialFunc(firstMsg.Addr, firstMsg.Data)`.
- `core/server/udp.go:92-111`: later packets in the same session take the current packet address and directly call `e.conn.WriteTo(dfMsg.Data, addr)` without re-running ACL or outbound policy evaluation.

In other words, destination selection is packet-scoped, but authorization is session-scoped.

## Impact

Any authenticated client that is allowed to use UDP relay can:

- open one UDP session using an allowed first destination;
- reuse the same session to send packets to destinations that ACL should reject;
- reach UDP services on `127.0.0.1` or on RFC1918/private-network addresses from the server's network perspective.

In real deployments, this can expose internal-only UDP services such as:

- internal DNS resolvers;
- service discovery endpoints;
- telemetry or metrics listeners;
- local administrative daemons;
- application-specific UDP services intended to be reachable only from localhost or the internal network.

This breaks the server's documented ACL-based UDP egress restrictions.

## Reproduction

Two cases were reproduced with integration tests.

### Case 1: localhost bypass

ACL:

```text
direct(127.0.0.1, udp/<allowedPort>)
reject(127.0.0.1/32)
```

Steps:

1. Start one UDP echo service on `127.0.0.1:<allowedPort>`.
2. Start another UDP echo service on `127.0.0.1:<blockedPort>`.
3. Connect an authenticated Hysteria client and create one UDP session.
4. Send a packet to the allowed loopback destination to establish the session.
5. Reuse the same UDP session and send a packet to the blocked loopback destination.

Observed result:

- The second packet is relayed successfully and the blocked loopback service replies.

Expected result:

- The second packet should be rejected because `127.0.0.1/32` is denied by ACL.

### Case 2: private-network bypass

ACL:

```text
direct(127.0.0.1, udp/<allowedPort>)
reject(10.0.0.0/8)
```

or the corresponding local RFC1918 range, such as `192.168.0.0/16` or `172.16.0.0/12`.

Steps:

1. Start one UDP echo service on `127.0.0.1:<allowedPort>`.
2. Start another UDP echo service on a real RFC1918 address of the server host.
3. Connect an authenticated Hysteria client and create one UDP session.
4. Send a packet to the allowed loopback destination first.
5. Reuse the same UDP session and send a packet to the RFC1918 destination.

Observed result:

- The private-address packet is relayed successfully and receives a reply.

Expected result:

- The packet should be rejected by ACL.

## PoC and local evidence

A local integration test file was added during verification:

- `core/internal/integration_tests/udp_private_acl_bypass_test.go`

The two tests are:

- `TestClientServerUDPACLBYPASSLoopback`
- `TestClientServerUDPACLBYPASSPrivateIPv4`

They can be executed with:

```bash
go test ./core/internal/integration_tests -run 'TestClientServerUDPACLBYPASS(Loopback|PrivateIPv4)' -count=1
```

The tests pass locally and demonstrate that a destination blocked by ACL becomes reachable after the session is established with an allowed first destination.

## Suggested fixes

Any of the following would address the issue:

1. Re-evaluate ACL and outbound policy for every defragmented UDP packet before forwarding it with `WriteTo`.
2. Alternatively, enforce a single immutable destination per UDP session and reject destination changes after the first packet.
3. Ensure logging and policy hooks are aligned with the chosen model so that policy enforcement and observability reflect the real per-packet destination.

## Severity assessment

Suggested CVSS v3.1 vector: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:L`

This reflects a network-reachable issue with low attack complexity, requiring only an authenticated client, no victim interaction, and allowing impact beyond the proxy process by exposing localhost and internal-network UDP resources from the server's trust boundary.

## References
- https://github.com/apernet/hysteria/security/advisories/GHSA-vgrc-hq28-p3xp
- https://github.com/apernet/hysteria
