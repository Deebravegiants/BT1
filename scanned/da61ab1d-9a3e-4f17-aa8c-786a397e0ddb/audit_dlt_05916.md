# [?] chore: fix vulnerabilities, remove unused deps, update packages

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-03-30
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/4aed1dbe9494750553c697c7ccc2263869c6ef11
Type: security-commit

## Details
chore: fix vulnerabilities, remove unused deps, update packages

- Fix all 15 npm audit vulnerabilities (0 remaining)
- Update lerna 9.0.5 -> 9.0.7
- Remove deprecated eslint-plugin-node and eslint-plugin-standard
- Remove unused deps from sign-client (@walletconnect/events, heartbeat)
- Remove unused deps from ethereum-provider (jsonrpc-http-connection, logger)
- Update @reown/appkit from pre-release to stable 1.8.19
- Apply minor/patch updates: @rollup/plugin-commonjs, @typescript-eslint/*,
  prettier, rollup, sinon, es-toolkit, wait-on
- Add @react-native-async-storage override to resolve peer dep conflict
- Regenerate clean lockfile without --legacy-peer-deps

Made-with: Cursor
