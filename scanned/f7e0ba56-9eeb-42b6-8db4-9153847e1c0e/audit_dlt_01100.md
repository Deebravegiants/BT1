# [M] ERC7984ERC20Wrapper: once a wrapper is filled, subsequent wrap requests do not revert and result in loss of funds.

## Summary
Severity: Medium
Chain: @openzeppelin/confidential-contracts
Component: @openzeppelin/confidential-contracts
CVE: CVE-2026-73645
CWE: Integer Overflow or Wraparound
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-hqf9-8xv5-x8xw
Type: github-advisory

## Details
### Impact
The `ERC7984` contract tracks total supply using a confidential `euint64` value. If a call to the internal `_mint` function would result in the total supply overflowing, the call fails silently. The `wrap` and `onTransferReceived` functions in `ERC7984ERC20Wrapper` assume that `_mint` won't fail silently and do not check the return value. If the mint function fails silently, users do not receive the confidential wrapped token but still send the underlying token, resulting in a loss of funds.

By default (without overriding `rate()`, the wrapper fills up after wrapping ~18.4 trillion tokens. There are very few tokens of value with sufficient total supply to result in the filling of the wrapper. That said, we recommend upgrading to `0.3.1` to remove this issue. 

### Patches
This issue has been patched in the `0.3.1` release.
