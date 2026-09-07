# [?] chore: update dependencies and fix security vulnerabilities

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-01-19
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/94dd2690d81f04b69e6e906f1e5964bac0c34ae5
Type: security-commit

## Details
chore: update dependencies and fix security vulnerabilities

- Update lerna 9.0.0 → 9.0.3
- Update sinon 14.0.0 → 21.0.1 and @types/sinon 10.0.13 → 21.0.0
- Update @typescript-eslint/* 8.30.1 → 8.53.0
- Update typescript 5.8.3 → 5.9.3
- Update prettier 3.5.3 → 3.8.0
- Update @changesets/* to latest patch versions
- Update eslint-config-prettier and eslint-plugin-prettier
- Update @aws-sdk/client-cloudwatch 3.450.0 → 3.971.0 (sign-client)
- Update @msgpack/msgpack 3.1.2 → 3.1.3 (utils)
- Update es-toolkit 1.39.3 → 1.44.0 (core, universal-provider)
- Update ethers to 6.16.0 and hardhat to 3.1.4 (providers)
- Align uint8arrays versions to 3.1.1 across all packages

Security fixes:
- Resolves AWS SDK region parameter vulnerability
- Resolves diff/sinon DoS vulnerability

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
