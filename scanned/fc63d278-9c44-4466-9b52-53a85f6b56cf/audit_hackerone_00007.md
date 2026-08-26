# [H] Restricted RPC Policy Bypass on ZMQ JSON-RPC Allows Unauthenticated Remote Admin Actions

## Summary
Severity: High (CVSS 8.2)
Program: Monero
Weakness: Improper Authentication - Generic
Reporter: usagirabbit
State: resolved
Disclosed: 2026-08-17T09:16:00.113Z
Source: https://hackerone.com/reports/3601469

## Details
## Summary

I found a high-severity access-control issue in Monero's ZMQ JSON-RPC surface.

When `monerod` is started in restricted/public-node mode, the HTTP RPC layer correctly suppresses admin-only methods, but the ZMQ JSON-RPC layer does not inherit or enforce that restriction. If an operator binds ZMQ beyond loopback, an unauthenticated remote client can invoke state-changing methods that the operator reasonably expects `--restricted-rpc` / `--public-node` to block.

The vulnerable flow is:

1. [README.md](README.md#L769) says public remote nodes must run with `--restricted-rpc`.
2. [src/daemon/command_line_args.h](src/daemon/command_line_args.h#L106) describes `--public-node` as "restricted RPC mode, view-only commands".
3. [src/rpc/core_rpc_server.h](src/rpc/core_rpc_server.h#L117) hides HTTP admin methods behind `!m_restricted`.
4. [src/daemon/daemon.cpp](src/daemon/daemon.cpp#L105) creates the ZMQ handler without propagating restricted-mode state in the vulnerable version.
5. [src/rpc/daemon_handler.cpp](src/rpc/daemon_handler.cpp#L941) dispatches the exposed ZMQ methods unconditionally in the vulnerable version.

This exposes the following restricted HTTP methods over ZMQ:

1. `start_mining`
2. `stop_mining`
3. `save_bc`
4. `set_log_level`
5. `mining_status`
6. `get_peer_list`

The highest-impact path is `start_mining`, because [src/rpc/daemon_handler.cpp](src/rpc/daemon_handler.cpp#L483) accepts an attacker-controlled payout address and attacker-controlled thread count up to `hardware_concurrency() * 4`.

 It is an RPC access-control bypass.

## Severity

Approximate CVSS v3.1: `8.1` with `AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H`.

I consider this `High`.

Why `8.1` is defensible:

1. The attacker is remote and unauthenticated.
2. The attack requires only a normal ZMQ JSON-RPC request once the operator has exposed ZMQ beyond loopback.
3. The affected methods cross a documented restricted/view-only boundary.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3601469_
