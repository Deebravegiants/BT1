# [H] Missing afterSwapReturnDelta Permission

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23359
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All swaps will revert if the dynamic protocol fee is enabled since hook-config.sol does not encode the afterSwapReturnDelta permission

Description: If AngstromL2::setPoolHookSwapFee is called by the owner to configure the dynamic hook protocol fee to a non-zero value then the Uniswap V4 delta accounting will result in a revert with CurrencyNotSettled(). This happens because the non-zero fee delta will be accounted to the hook:
```solidity
if (feeCurrencyId == NATIVE_CURRENCY_ID) {
    unclaimedProtocolRevenueInEther += fee.toUint128();
    @> UNI_V4.mint(address(this), feeCurrencyId, fee + taxInEther);
} else {
    @> UNI_V4.mint(address(this), feeCurrencyId, fee);
    UNI_V4.mint(address(this), NATIVE_CURRENCY_ID, taxInEther);
}
```
However, hook-config.sol does not specify that the afterSwapReturnDelta permission should be encoded within the hook address, so it is possible to construct the contract without it:
```solidity
Hooks.validateHookPermissions(IHooks(address(this)), getRequiredHookPermissions());
```
With this omission, the permission is false and so the unspecified hook delta is not parsed, meaning the intended afterSwap() return delta is not added to the caller delta and the additional protocol fee is not paid:
```solidity
if (self.hasPermission(AFTER_SWAP_FLAG)) {
    hookDeltaUnspecified += self.callHookWithReturnDelta(
        abi.encodeCall(IHooks.afterSwap, (msg.sender, key, params, swapDelta, hookData)),
        @> self.hasPermission(AFTER_SWAP_RETURNS_DELTA_FLAG)
    ).toInt128();
}
```
```solidity
function callHookWithReturnDelta(IHooks self, bytes memory data, bool parseReturn) internal returns (int256) {
    bytes memory result = callHook(self, data);
    // If this hook wasn't meant to return something, default to 0 delta
    @> if (!parseReturn) return 0;
    // A length of 64 bytes is required to return a bytes4, and a 32 byte delta
    if (result.length != 64) InvalidHookResponse.selector.revertWith();
    return result.parseReturnDelta();
}
```

Impact: All swaps will revert if the dynamic protocol fee is enabled.

## Proof of Concept
The following test should be added to AngstromL2.t.sol
```solidity
function test_cyfrin_SwapFeeNotSettledBecauseHookConfigMissing() public {
    PoolKey memory key = initializePool(address(token), 10, 3);
    angstrom.setPoolHookSwapFee(key, 0.005e6); // 0.5%
    addLiquidity(key, 0, 10, 1e22);
    vm.expectRevert(bytes4(keccak256("CurrencyNotSettled()")));
    router.swap(key, true, -10e18, int24(0).getSqrtPriceAtTick());
}
```

## Recommendation
Recommended Mitigation: The following permission should be added to hooks-config.sol:
```solidity
permissions.afterSwapReturnDelta = true;
```
