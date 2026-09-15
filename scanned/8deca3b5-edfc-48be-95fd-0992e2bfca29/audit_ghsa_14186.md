# [M] `chainId` may be outdated if user changes chains as part of connection in @web3-react

## Summary
Severity: Medium
Advisory: GHSA-8pf3-6fgr-3g3g
CVE: CVE-2023-30543
CWE: CWE-362
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2023-04-18
Source: https://github.com/advisories/GHSA-8pf3-6fgr-3g3g
Type: github-advisory

## Affected
- npm: `@web3-react/coinbase-wallet` — affected >=6.0.0 <8.0.35-beta.0
- npm: `@web3-react/eip1193` — affected >=6.0.0 <8.0.27-beta
- npm: `@web3-react/metamask` — affected >=6.0.0 <8.0.30-beta.0
- npm: `@web3-react/walletconnect` — affected >=6.0.0 <8.0.37-beta.0

## Details
### Impact
`chainId` may be outdated if the user changes chains as part of the connection flow. This means that the value of `chainId` returned by `useWeb3React()` may be incorrect. In an application, this means that any data derived from `chainId` could be incorrect.

For example, if a swapping application derives a wrapped token contract address from the `chainId` *and* a user has changed chains as part of their connection flow the application could cause the user to send funds to the incorrect address when wrapping. This is a common approach when using other foundational libraries like [`ethers`](https://github.com/ethers-io/ethers.js), and most users of v8 will want to upgrade past the affected versions.

### Patches
Patched in https://github.com/Uniswap/web3-react/pull/749.
Users of web3-react@8.0.x-beta.0 should upgrade to at least:
 - @web3-react/coinbase-wallet@^8.0.35-beta.0
 - @web3-react/eip1193@^8.0.27-beta.0
 - @web3-react/metamask@^8.0.30-beta.0
 - @web3-react/walletconnect@^8.0.37-beta.0

### Workarounds
N/A

### References
N/A

## References
- https://github.com/Uniswap/web3-react/security/advisories/GHSA-8pf3-6fgr-3g3g
- https://nvd.nist.gov/vuln/detail/CVE-2023-30543
- https://github.com/Uniswap/web3-react/pull/749
- https://github.com/Uniswap/web3-react
