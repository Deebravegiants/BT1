# [M] `weth.withdrawTo` is only implemented in Arbitrum so protocol wont wqork in other network

## Summary
Severity: Medium
Reporter: 0x4non
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L704
Type: audit-issue

## Details
# `weth.withdrawTo` is only implemented in Arbitrum so protocol wont wqork in other network

## Summary

Issue regarding the specific implementation of the withdraw_from_account_eth method in the Vault contract, limiting its functionality to the Arbitrum network. Method `weth.withdrawTo` is defined on Arbitrum weth implementation.

## Vulnerability Detail

The Vault contract's `withdraw_from_account_eth` method calls `withdrawTo` on the WETH contract. However, the `withdrawTo` function is only implemented in the WETH version deployed on the Arbitrum network. This means the protocol's functionality is currently limited to this specific network. In a conversation with **0xNic**, it was mentioned that "other networks might come later", indicating this might be a design choice rather than an oversight, but still a point of potential enhancement.

## Impact

The protocol cannot operate on other Ethereum compatible networks such as Ethereum mainnet or other Layer 2 solutions. This restricts the user base of the protocol to Arbitrum only. It also presents a dependency on the Arbitrum network's stability and might hamper potential expansion plans.

## Code Snippet

[contracts/margin-dex/Vault.vy#L704](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/Vault.vy#L704)
```vy
@nonreentrant("lock")
@external
def withdraw_from_account_eth(_amount: uint256):
    """
    @notice
        Allows a user to withdraw from his WETH margin and
        automatically swaps back to ETH.
    """
    assert self.margin[msg.sender][WETH] >= _amount, "insufficient balance"
    self.margin[msg.sender][WETH] -= _amount
    raw_call(
        WETH,
        concat(
            method_id("withdrawTo(address,uint256)"),
            convert(msg.sender, bytes32),
            convert(_amount, bytes32),
        ),
    )
    log WithdrawBalance(msg.sender, WETH, _amount)
```

## Tool used

Manual Review

## Recommendation

Instead of `withdrawTo`, you should first `withdraw` and then do `safeTransferETH` to the user.

This is a solidity example but can be easily adapted to vyper:
```solidity
// WETH9.withdrawTo(recipient, amount);
receive() external payable {
    require(msg.sender == address(WETH));
}
// ...
WETH9.withdraw(amount);
SafeTransferLib.safeTransferETH(recipient, amount);
```
