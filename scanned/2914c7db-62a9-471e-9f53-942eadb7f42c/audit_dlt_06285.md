# [M] `reserveFactor` validation check cannot revert in case of invalid value assignment.

## Summary
Severity: Medium
Chain: Smart contract
Component: Ion-Protocol
Published: 2024-01-24
Source: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/39
Type: hats-finding

## Details
**Github username:** @rokinot
**Twitter username:** rokinot
**Submission hash (on-chain):** 0xabb9bb8fac1047482581deb355734c20418de93250ea4c26f2e340418ce76c4e
**Severity:** medium

**Description:**
**Description**\
In [InterestRate.sol](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/blob/bdfcb2aeb948d5c658f61636f8674459cd538c26/src/InterestRate.sol#L159-L162), some checks are done in order to ensure variables were assigned with valid inputs. `reserveFactor` is one of them, which is an ` uint16` type. This value is then checked against `RAY` as shown in the link. The issue is, since `RAY` is equal to `1e27`, an amount much higher than what the uint16 type allows for, the revert section is unreachable regardless of inputed value.

Now that the check will always pass, the interest rate module can be updated with any reserve factor. In [IonPool.sol](https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/blob/bdfcb2aeb948d5c658f61636f8674459cd538c26/src/IonPool.sol#L514), when interest has to be accrued, it calls `_calculateRewardAndDebtDistributionForIlk()`where it runs a subtraction of `RAY - reserveFactor.scaledUpToRay(4)`. This scale up is equivalent to multiplying the reserve factor by `10**23`.

If the interest rate module is updated with a new `reserveFactor` of amount higher than 10000, `_accrueInterest()` will always revert due to underflow, and as a consequence so will `pause()` `supply()`, `withdraw()`, `depositCollateral()`, `withdrawCollateral()`, `borrow()`, `repay()` and `confiscateVault()`, freezing all operations that can move the funds of a pool.

**Attachments**

1. **Proof of Concept (PoC) File**\
Run the test below under `IonPool.t.sol`

```solidity
    function test_InvalidReserveFactorIsSet() external {
        uint256 collateralDepositAmount = 1e18;
        uint256 normalizedBorrowAmount = 1e18;

        uint8 i = 0; //we'll use the first index

        //simulate a borrow
        vm.prank(borrower1);
        ionPool.depositCollateral(i, borrower1, borrower1, collateralDepositAmount, new bytes32[](0));

        vm.prank(borrower1);
        ionPool.borrow(i, borrower1, borrower1, normalizedBorrowAmount, new bytes32[](0));

        ilkConfigs[i].reserveFactor = 10_001; //any value above 10_000 will cause it to revert

        InterestRate newInterestRateModule = new InterestRate(ilkConfigs, apyOracle);

        ionPool.updateInterestRateModule(newInterestRateModule);

```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Ion-Protocol-0x20c44e7b618d58f9982e28de66d8d6ee176eb481/issues/39_
