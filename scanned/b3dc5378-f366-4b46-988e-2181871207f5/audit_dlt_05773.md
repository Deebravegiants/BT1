# [H] The ZeroLendToken contract in the Governance mo...

## Summary
Severity: High
Chain: Smart contract
Component: ZeroLend
Source: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/29019%20-%20%5BSC%20-%20High%5D%20The%20ZeroLendToken%20contract%20in%20the%20Governance%20mo....md
Type: immunefi-boost

## Details
Target: https://github.com/zerolend/governance

## Description

## Brief/Intro

The ZeroLendToken contract in the Governance module mishandles the whitelist. It is treated as a blacklist.

## Vulnerability Details

The code below handles updating of the balance when a token is sent by `from` to `to`.

```
function _update(
    address from,
    address to,
    uint256 value
) internal virtual override {
    require(!blacklisted[from] && !blacklisted[to], "blacklisted");
    require(!paused && !whitelisted[from], "paused");
    super._update(from, to, value);
}
```

Note that if `whitelisted` is True, the token should allow the transfer. However the condition is flipped, so it will certainly abort the transfer.

## Impact Details

A whitelisted user will not be able to transfer their tokens, resulting in a temporary freezing of funds.

## Recommended remidiation

Consider refactoring the code as suggestedbelow: `require(!paused || whitelisted[from])`

## References

https://github.com/zerolend/governance/blob/a30d8bb825306dfae1ec5a5a47658df57fd1189b/contracts/ZeroLendToken.sol#L61


_Trimmed to 38 lines — full report: https://github.com/immunefi-team/Past-Audit-Competitions/blob/main/ZeroLend/29019%20-%20%5BSC%20-%20High%5D%20The%20ZeroLendToken%20contract%20in%20the%20Governance%20mo....md_
