# [M] Regular users are not incentivized to liquidate

## Summary
Severity: Medium
Reporter: twicek
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L373
Type: audit-issue

## Details
# Regular users are not incentivized to liquidate

## Summary
Liquidation penalty fee is distributed between LPs and the protocol even when an external actor calls the function.

## Vulnerability Detail
Keeper bots are supposed to execute liquidations when positions are unhealthy, but anyone can perform a liquidation. In fact, only the protocol via its keeper bots is incentivized to perform liquidation since reward are only distributed to LPs and the protocol:

[Vault.vy#L346-L373](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L346-L373)
```solidity
def liquidate(_position_uid: bytes32):
				...
        self._distribute_trading_fee(position.debt_token, penalty)
```

[Vault.vy#L1342-L1356](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1342-L1356)
```solidity
def _distribute_trading_fee(_token: address, _amount: uint256):
    """
    @notice
        Distributes _amount of _token between LPs and protocol.
    """
    amount_for_lps: uint256 = _amount * self.trading_fee_lp_share / PERCENTAGE_BASE
    amount_for_protocol: uint256 = _amount - amount_for_lps


    if amount_for_lps > 0:
        self._pay_interest_to_lps(_token, amount_for_lps)
        log TradingFeeDistributed(0x0000000000000000000000000000000000000001, _token, amount_for_lps) # special address logged to signal LPs
    
    if amount_for_protocol > 0:
        self._safe_transfer(_token, self.protocol_fee_receiver, amount_for_protocol)
        log TradingFeeDistributed(self.protocol_fee_receiver, _token, amount_for_protocol)
```

If a regular user wants to liquidate an unhealthy position, he will not receive any rewards for doing so. Even a LP will only receive rewards diluted between all LPs and the protocol which is not enough of an incentive.

## Impact
Protocol Keepers are the only actors incentivized to liquidate unhealthy positions. Any issue in the keeper monitoring service availability could lead to positions aggregating bad debt.

## Code Snippet
[Vault.vy#L1342-L1356](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L1342-L1356)

## Tool used

Manual Review

## Recommendation
Consider rewarding the liquidator fully when it is not a keeper bot.
