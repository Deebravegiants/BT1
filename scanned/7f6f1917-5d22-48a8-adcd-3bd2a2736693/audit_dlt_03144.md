# [M] Tokens with fee on transfer are not supported in `PublicVault.sol`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-01-astaria
Published: 2023-01-19
Source: https://github.com/code-423n4/2023-01-astaria-findings/issues/424
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-astaria/blob/main/src/PublicVault.sol#L251-L265
https://github.com/code-423n4/2023-01-astaria/blob/main/src/PublicVault.sol#L148-L190
https://github.com/code-423n4/2023-01-astaria/blob/main/src/PublicVault.sol#L148


# Vulnerability details

### Description

Some tokens take a transfer fee (e.g. `STA`, `PAXG`), some do not currently charge a fee but may do so in the future (e.g. `USDT`, `USDC`).

Should a fee-on-transfer token be added to the `PublicVault`, the tokens will be locked in the `PublicVault.sol` contract. Depositors will be unable to withdraw their rewards.
In the current implementation, it is assumed that the received amount is the same as the transfer amount. However, due to how fee-on-transfer tokens work, much less will be received than what was transferred.
As a result, later users may not be able to successfully withdraw their shares, as it may revert at https://github.com/code-423n4/2023-01-astaria/blob/main/src/PublicVault.sol#L148 when `WithdrawProxy` is called due to insufficient balance.

### Proof of Concept

i.e. Fee-on-transfer scenario:
Contract calls transfer from contractA 100 tokens to current contract
Current contract thinks it received 100 tokens
It updates balances to increase +100 tokens
While actually contract received only 90 tokens
That breaks whole math for given token



```solidity
  function deposit(uint256 amount, address receiver)
    public
    override(ERC4626Cloned)
    whenNotPaused
    returns (uint256)
  {
    VIData storage s = _loadVISlot();
    if (s.allowListEnabled) {
      require(s.allowList[receiver]);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-astaria-findings/issues/424_
