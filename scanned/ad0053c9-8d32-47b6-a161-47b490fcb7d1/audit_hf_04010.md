# [H] Native ETH not received when removing liquidity

## Summary
Severity: High
Contest weight: 0.7873
Dataset id: 20410
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Native ETH was not received when removing liquidity from Curve V2 pools due to the mishandling of Native ETH and WETH, leading to a loss of assets. Curve V2 pool will always wrap to WETH and send to leverage vault unless the use_eth is explicitly set to True. Otherwise, it will default to False. The following implementation of the remove_liquidity_one_coin function taken from one of the Curve V2 pools shows that unless the use_eth is set to True, the WETH.deposit() will be triggered to wrap the ETH, and WETH will be transferred back to the caller. The same is true for the remove_liquidity function, but it is omitted for brevity.
https://etherscan.io/address/0x0f3159811670c117c372428d4e69ac32325e4d0f#code
```python
def remove_liquidity_one_coin(token_amount: uint256, i: uint256, min_amount: uint256,
    use_eth: bool = False, receiver: address = msg.sender) -> uint256:
    A_gamma: uint256[2] = self._A_gamma()
    dy: uint256 = 0
    D: uint256 = 0
    p: uint256 = 0
    xp: uint256[N_COINS] = empty(uint256[N_COINS])
    future_A_gamma_time: uint256 = self.future_A_gamma_time
    dy, p, D, xp = self._calc_withdraw_one_coin(A_gamma, token_amount, i, (future_A_gamma_time > 0), True)
    assert dy >= min_amount, "Slippage"
    if block.timestamp >= future_A_gamma_time:
        self.future_A_gamma_time = 1
    self.balances[i] -= dy
    CurveToken(self.token).burnFrom(msg.sender, token_amount)
    coin: address = self.coins[i]
    if use_eth and coin == WETH20:
        raw_call(receiver, b"", value=dy)
    else:
        if coin == WETH20:
            WETH(WETH20).deposit(value=dy)
            coin,
            _abi_encode(receiver, dy, method_id=method_id("transfer(address,uint256)")),
            max_outsize=32,
```
Notional's Leverage Vault only works with Native ETH. It was found that the remove_liquidity_one_coin and remove_liquidity functions are executed without explicitly setting the use_eth parameter to True. Thus, WETH instead of Native ETH will be returned during remove liquidity. As a result, these WETH will not be accounted for in the vault and result in a loss of assets.
```solidity
function _unstakeAndExitPool(
..SNIP..
    ICurve2TokenPool pool = ICurve2TokenPool(CURVE_POOL);
    exitBalances = new uint256[](2);
    if (isSingleSided) {
        // Redeem single-sided
        exitBalances[_PRIMARY_INDEX] = pool.remove_liquidity_one_coin(
            poolClaim, int8(_PRIMARY_INDEX), _minAmounts[_PRIMARY_INDEX]
        );
    } else {
        length array
        uint256[2] memory minAmounts;
        minAmounts[0] = _minAmounts[0];
        minAmounts[1] = _minAmounts[1];

        uint256[2] memory _exitBalances = pool.remove_liquidity(poolClaim, minAmounts);
        exitBalances[0] = _exitBalances[0];
        exitBalances[1] = _exitBalances[1];
    }
```
Following are some of the impacts due to the mishandling of Native ETH and WETH during liquidity removal in Curve pools, leading to loss of assets:
1. Within the redeemFromNotional, if the vaults consist of ETH, the _UNDERLYING_IS_ETH will be set to true. In this case, the code will attempt to call transfer to transfer Native ETH, which will fail as Native ETH is not received and users/Notional are unable to redeem.
```solidity
function redeemFromNotional(
..SNIP..
    if (_UNDERLYING_IS_ETH) {
        if (transferToReceiver > 0)
            payable(receiver).transfer(transferToReceiver);
        if (transferToNotional > 0)
            payable(address(NOTIONAL)).transfer(transferToNotional);
    } else {
..SNIP..
```
2. WETH will be received instead of Native ETH during the emergency exit. During vault restoration, WETH is not re-entered into the pool as only Native ETH residing in the vault will be transferred to the pool. Leverage vault only works with Native ETH, and if one of the pool tokens is WETH, it will be converted to Native ETH (0x0 or 0xEeeee) during deployment/initialization. Thus, the WETH is stuck in the vault. This causes the value per share to drop significantly. (Reference)
```solidity
function emergencyExit(
    uint256 claimToExit, bytes calldata /* data */
) external override onlyRole(EMERGENCY_EXIT_ROLE) {
    StrategyVaultState memory state = VaultStorage.getStrategyVaultState();
    if (claimToExit == 0) claimToExit = state.totalPoolClaim;

    // By setting min amounts to zero, we will accept whatever tokens come from the pool
    // in a proportional exit. Front running will not have an effect since no trading will
    // occur during a proportional exit.
    _unstakeAndExitPool(claimToExit, new uint256[](NUM_TOKENS()), true);

    state.totalPoolClaim = state.totalPoolClaim - claimToExit;
    state.setStrategyVaultState();
```

## Recommendation
If one of the pool tokens is ETH, consider setting is_eth to true when calling remove_liquidity_one_coin and remove_liquidity functions to ensure that Native ETH is sent back to the vault.
