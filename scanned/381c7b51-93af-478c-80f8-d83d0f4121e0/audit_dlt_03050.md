# [M] Curve Strategy Yield can be Lost by Griefing due to Delta Balance Check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1429
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoNativeStrategy.sol#L151-L156


# Vulnerability details

### Impact
`TricryptoLPStrategy-compound` computes the amount of `CRV` to Sell as:
`uint256 crvAmount = crvBalanceAfter - crvBalanceBefore;`

https://github.com/Tapioca-DAO/tapioca-yieldbox-strategies-audit/blob/05ba7108a83c66dada98bc5bc75cf18004f2a49b/contracts/curve/TricryptoNativeStrategy.sol#L151-L156
```solidity
    function compound(bytes memory) public {
        uint256 claimable = lpGauge.claimable_tokens(address(this));
        if (claimable > 0) {
            uint256 crvBalanceBefore = rewardToken.balanceOf(address(this));
            minter.mint(address(lpGauge));
            uint256 crvBalanceAfter = rewardToken.balanceOf(address(this));

            if (crvBalanceAfter > crvBalanceBefore) {
                uint256 crvAmount = crvBalanceAfter - crvBalanceBefore;
```

This assumes that `minter.mint(address(lpGauge));` will cause tokens to be sent to the Strategy

However, a griefer could call `claim_rewards(STRATEGY):` to cause the `CRV` to be sent directly to it before a call to `compound` is made.

This breaks the check (since it will result in a 0)

And causes total Loss of Yield


### POC
- Attacker calls `claim_rewards(STRATEGY)`
- The Strategy no longer compounds the rewards

### Code from Curve Gauge

https://arbiscan.io/address/0x555766f3da968ecbefa690ffd49a2ac02f47aa5f#code#L544

```solidity
@external
@nonreentrant('lock')
def claim_rewards(_addr: address = msg.sender, _receiver: address = ZERO_ADDRESS):
    """
    @notice Claim available reward tokens for `_addr`
    @param _addr Address to claim for
    @param _receiver Address to transfer rewards to - if set to
                     ZERO_ADDRESS, uses the default reward receiver
                     for the caller
    """
    if _receiver != ZERO_ADDRESS:
        assert _addr == msg.sender  # dev: cannot redirect when claiming for another user
    self._checkpoint_rewards(_addr, self.totalSupply, True, _receiver)
```

As you can see the gauge allows claiming on behalf, which will break the delta check from the Strategy

### Mitigation

Use the absolute value for Curve or similar reward tokens, also consider adding a sweep function while protecting the deposit tokens



## Assessed type

ERC4626
