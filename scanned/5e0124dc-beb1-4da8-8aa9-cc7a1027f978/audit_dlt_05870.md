# [?] chore: Upgrade rustls to fix security vulnerability (#3331)

## Summary
Severity: Unknown
Chain: zkSync
Component: matter-labs/zksync-era
Published: 2024-11-25
Source: https://github.com/matter-labs/zksync-era/commit/193c855fc593f53b63d3eab9784ee2dae255205c
Type: security-commit

## Details
chore: Upgrade rustls to fix security vulnerability (#3331)

## What ❔
Upgrade rustls

## Why ❔
```
error[vulnerability]: rustls network-reachable panic in `Acceptor::accept`
    ┌─ /github/workspace/Cargo.lock:601:1
    │
601 │ rustls 0.23.16 registry+https://github.com/rust-lang/crates.io-index
    │ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ security vulnerability detected
    │
    ├ ID: RUSTSEC-[20](https://github.com/matter-labs/zksync-era/actions/runs/12011183823/job/33479628638?pr=3199#step:4:21)24-0399
    ├ Advisory: https://rustsec.org/advisories/RUSTSEC-2024-0399
    ├ A bug introduced in rustls 0.23.13 leads to a panic if the received
      TLS ClientHello is fragmented.  Only servers that use
      `rustls::server::Acceptor::accept()` are affected.
      
      Servers that use `tokio-rustls`'s `LazyConfigAcceptor` API are affected.
      
      Servers that use `tokio-rustls`'s `TlsAcceptor` API are not affected.
      
      Servers that use `rustls-ffi`'s `rustls_acceptor_accept` API are affected.
    ├ Announcement: https://github.com/rustls/rustls/issues/[22](https://github.com/matter-labs/zksync-era/actions/runs/12011183823/job/33479628638?pr=3199#step:4:23)27
    ├ Solution: Upgrade to >=0.[23](https://github.com/matter-labs/zksync-era/actions/runs/12011183823/job/33479628638?pr=3199#step:4:24).18 (try `cargo update -p rustls`)
```
