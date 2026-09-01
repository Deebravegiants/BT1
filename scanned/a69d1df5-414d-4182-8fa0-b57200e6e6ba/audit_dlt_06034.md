# [?] chore(wallet, docs, ts-sdk): Fix GHSA-43fc-jf86-j433: Upgrade axios to 1.13.5 (#10186)

## Summary
Severity: Unknown
Chain: IOTA
Component: iotaledger/iota
Published: 2026-02-12
Source: https://github.com/iotaledger/iota/commit/c04074695cc5eaf5dfc110f7a16546a91ca7aff2
Type: security-commit

## Details
chore(wallet, docs, ts-sdk): Fix GHSA-43fc-jf86-j433: Upgrade axios to 1.13.5 (#10186)

# Description of change

Fixes high severity DoS vulnerability in axios <=1.13.4 where
`mergeConfig` allows `__proto__` key manipulation.

## Changes

- Upgraded axios from `^1.12.0` to `^1.13.5` in:
  - `apps/wallet/package.json`
  - `docs/site/package.json`
  - `sdk/ledgerjs-hw-app-iota/package.json`
- Updated `pnpm-lock.yaml`

## How the change has been tested

Verified axios 1.13.5 is installed in all three packages via `pnpm list
axios`. The vulnerable 1.12.0 version is no longer present in the
dependency tree.

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more
addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by
firewall rules:
>
> - `downloads.sentry-cdn.com`
> - Triggering command:
`/home/REDACTED/work/_temp/ghcca-node/node/bin/node node
./scripts/install.js` (dns block)
>
> If you need me to access, download, or install something from one of
these locations, you can either:
>

_Trimmed to 38 lines — full report: https://github.com/iotaledger/iota/commit/c04074695cc5eaf5dfc110f7a16546a91ca7aff2_
