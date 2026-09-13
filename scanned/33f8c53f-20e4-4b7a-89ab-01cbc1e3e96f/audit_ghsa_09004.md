# [H] Netty epoll transport denial of service via RST on half-closed TCP connection

## Summary
Severity: High
Advisory: GHSA-rwm7-x88c-3g2p
CVE: CVE-2026-42577
CWE: CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-rwm7-x88c-3g2p
Type: github-advisory

## Affected
- Maven: `io.netty:netty-transport-classes-epoll` — affected >=4.2.0.Final <4.2.13.Final

## Details
## Summary

Netty's epoll transport fails to detect and close TCP connections that receive a RST after being half-closed, leading to stale channels that are never cleaned up and, in some code paths, a 100% CPU busy-loop in the event loop thread.

## Affected versions

All versions of 4.2.x `netty-transport-classes-epoll` up to and including 4.2.12.Final

## Fixed in

4.2.13.Final (fix merged into the `4.2` branch via [#16689](https://github.com/netty/netty/pull/16689); release not yet cut as of 2026-04-25).

## Severity

**Medium** — Denial of Service (resource exhaustion / CPU spin)

**CVSS:** 3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H - **7.5**

**CWE:** CWE-772: Missing Release of Resource after Effective Lifetime

## Description

When a TCP connection using Netty's epoll transport has `ALLOW_HALF_CLOSURE` enabled (or is in a half-closed state via the HTTP codec), and the remote peer:

1. Sends a FIN (half-close), causing the server to mark the input as shutdown, then
2. Sends a RST (e.g. by closing with `SO_LINGER=0`)

the server-side channel is never closed. This happens because:

- `epollOutReady()` is a no-op when there is no pending flush.
- `epollInReady()` short-circuits via `shouldBreakEpollInReady()` because input is already marked as shutdown.
- The `EPOLLERR`/`EPOLLHUP` error condition is therefore never processed, and `channelInactive` is never fired.

Depending on the Netty version and configuration, this results in:

- **Stale channels**: The connection is never closed or deregistered. An unauthenticated remote attacker can repeat the sequence to accumulate stale connections, exhausting file descriptors, memory, or connection-count limits.
- **CPU busy-loop**: In code paths where `clearEpollIn0()` is not called during the `ChannelInputShutdownReadComplete` event, `epoll_wait` returns immediately on every iteration for the affected fd, causing 100% CPU utilization on the event loop thread and starving all other connections multiplexed on it.

## Mitigation

- Upgrade to 4.2.13.Final when released (or build from the `4.2` branch at commit [`0ec3d97`](https://github.com/netty/netty/commit/0ec3d97fab376e243d328ac95fbd288ba0f6e22d)).
- If upgrading is not immediately possible, configure idle timeouts on connections to limit the lifetime of stale channels.

## References

- Issue: https://github.com/netty/netty/issues/16683
- Fix: https://github.com/netty/netty/pull/16689

## References
- https://github.com/netty/netty/security/advisories/GHSA-rwm7-x88c-3g2p
- https://nvd.nist.gov/vuln/detail/CVE-2026-42577
- https://github.com/netty/netty/pull/16689
- https://github.com/netty/netty/commit/0ec3d97fab376e243d328ac95fbd288ba0f6e22d
- https://github.com/netty/netty
