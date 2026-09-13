# [M] There may be a lesser amount of Aave aTokens than what is tracked in the OrigamiAaveV3BorrowAndLend.

## Summary
Severity: Medium
Chain: Smart contract
Component: Origami
Published: 2024-03-01
Source: https://github.com/hats-finance/Origami-0x998f1b716a5022be026ca6b919c0ddf45ca31abd/issues/52
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x710b245526ff7b98f3a018e697215f57c7f0451d132e35e912f4bfe7ea657837
**Severity:** medium

**Description:**
**Description**\
In any `protocol`, certain main `invariants` are expected to be maintained. 
During normal `audit` competitions in many platforms , a list of these `invariants` is typically established, and any violation is considered a vulnerability, at least of `medium` severity.

Likewise, I believe the `Origami protocol` also has some key `invariants`. 
One of the important `main invariants` of the `Origami protocol`, in my view, is as follows:

`The suppliedBalance tracked in the OrigamiAaveV3BorrowAndLend should never be less than the actual balance.` 

The `actual balance` comprises the sum of the `balance tracked manually` and the `donated tokens`. 
Thus, it is essential that there always exists a larger actual `balance` than the `suppliedBalance`.
Several functions within the `protocol` including `reservesBalance`, `_maxRedeemFromReserves` and `_validateAfterRebalance` functions rely on `suppliedBalance` value, and in the worst-case scenario, a `withdrawal` could potentially be reverted due to a lack of `1 wei`.

While I cannot enumerate all the `potential impacts` here, I firmly believe that maintaining this `main invariant` is crucial and should receive an appropriate level of attention.

**Attack Scenario**\
I will describe the process through an example accompanied by mathematical calculations.

In `AaveAToken`, the following relationship exists between the `balance` and `scaledBalance`.
```
function balanceOf(
    address user
  ) public view virtual override(IncentivizedERC20, IERC20) returns (uint256) {
    return super.balanceOf(user).rayMul(POOL.getReserveNormalizedIncome(_underlyingAsset));
  }
```
The `POOL.getReserveNormalizedIncome(_underlyingAsset)` represents the `current index`, and the `rayMul` formula is as follows:
```
function rayMul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    // to avoid overflow, a <= (type(uint256).max - HALF_RAY) / b
    assembly {
      if iszero(or(iszero(b), iszero(gt(a, div(sub(not(0), HALF_RAY), b))))) {
        revert(0, 0)
      }

      c := div(add(mul(a, b), HALF_RAY), RAY)
    }
}
```
i.e
```
rayMul(a, b) = (a * b + RAY / 2) / RAY;
uint256 internal constant RAY = 1e27;
```

Suppose the current `tracked _aTokenShares` is `5555555555555555500`. (label as `B`)
Based on this value, we can calculate the `suppliedBalance`. 
For convenience, I logged some test results.
```
Current Index                           ====>    1000039826138980826350362068
The tracked scaledBalance     ====>    5555555555555555500
The tracked suppliedBalance  ====>    5555776811883226757
```
There are some `donated tokens`, for example, `3000000000000000000` (labeld as `A`).
After the donation:
```
Total scaledBalance          ====>    8555555555555555500
Total Balance                     ====>    8555896290300169237
```
Mathematically
```
suppliedBalance = (B * index + RAY / 2) / RAY;
donatedTokens = (A * index + RAY / 2) / RAY;

current scaledBalance = B + A
current balance = ((B + A) * index + RAY / 2) / RAY;
```
Then the `reclaimable` token amount can be calculated as `aaveAToken.balanceOf(address(this)) - suppliedBalance()`.
This will be the standard procedure to reclaim the excess amount.
```
function recoverToken(address token, address to, uint256 amount) external onlyElevatedAccess {       
    // If the token to recover is the aaveAtoken, can only remove any *surplus* reserves (ie donation reserves).
    // It can't dip into the actual user added reserves. 
    if (token == address(aaveAToken)) {
        uint256 bal = aaveAToken.balanceOf(address(this));
        if (amount > (bal - suppliedBalance())) revert CommonEventsAndErrors.InvalidAmount(token, amount);
    }

    emit CommonEventsAndErrors.TokenRecovered(to, token, amount);
    IERC20(token).safeTransfer(to, amount);
}
```
Due to the calculation of `balance` from `scaledBalance` considering `RAY / 2`, the difference between the `current balance` and the `tracked balance` can be larger than the `donated amount` (maybe `1 wei`).
```
aaveAToken.balanceOf(address(this)) - suppliedBalance() = ((B + A) * index + RAY / 2) / RAY - (B * index + RAY / 2) / RAY > (A * index + RAY / 2) / RAY;
```
You can view the result in the comment.
```
The donated token amount      ====>    3000119478416942479
The clamiable token amount   ====>    3000119478416942480
```
And in the transfer of `AaveAToken`, we can calculate `scaledBalance` from `balance` as shown below:
```
function _transfer(address sender, address recipient, uint256 amount, uint256 index) internal {
    super._transfer(sender, recipient, amount.rayDiv(index).toUint128());
}
```
The `rayDiv` formula is 
```
function rayDiv(uint256 a, uint256 b) internal pure returns (uint256 c) {
    // to avoid overflow, a <= (type(uint256).max - halfB) / RAY
    assembly {
      if or(iszero(b), iszero(iszero(gt(a, div(sub(not(0), div(b, 2)), RAY))))) {
        revert(0, 0)
      }

      c := div(add(mul(a, RAY), div(b, 2)), b)
    }
}
```
i.e.
```
rayDiv(a, b) = (a * RAY + b / 2) / b;
a = ((B + A) * index + RAY / 2) / RAY - (B * index + RAY / 2) / RAY;
b = index;
```
We are attempting to reclaim an amount `1 wei` larger than exact, and this calculation also considers `index / 2`, resulting in the deduction of the larger `scaledBalance`.
```
Current balance                        ====>    5555776811883226756
The tracked suppliedBalance  ====>    5555776811883226757
```
This issue may not be problematic in other cases because there is only a `1 wei` gap, and there is a mathematical proof that there is no `underflow` when transferring all the balance in `AaveAToken`.
```
Current Scaled Balance : S;
Current Balance : C = (S * index + RAY / 2) / RAY;

When transfer all balance, the removed scaledBalance is
(C * RAY + index / 2) / index <= (((S * index + RAY / 2) / RAY) * RAY + index / 2) <= (S * index + RAY / 2 + index / 2) / index <= S. (from RAY < index)
```

But in the `Origami` protocol, we manually track the `balance` that belongs to the `protocol`, so we must ensure that this value is at least equal to the `current balance`.

Please add below test file into `OrigamiAaveV3BorrowAndLend.t`:
```
function test_suppliedBalance_invariant() public {
        uint256 RAY = 1e27;
        uint256 index = borrowLend.aavePool().getReserveNormalizedIncome(address(wstEthToken));
        
        console.log("Current Index                ===>   ", index);
        uint256 B = 5555555555555555500;
        uint256 amount1 = (B * index + RAY / 2) / RAY;
        supply(amount1);

        assertEq(borrowLend.aaveAToken().scaledBalanceOf(address(borrowLend)), B);

        console.log("The tracked scaledBalance    ====>   ", borrowLend.aaveAToken().scaledBalanceOf(address(borrowLend)));
        console.log("The tracked suppliedBalance  ====>   ", borrowLend.suppliedBalance());

        uint256 A = 3000000000000000000;
        uint256 amount2 = (A * index + RAY / 2) / RAY;
        
        vm.startPrank(alice);
        doMint(wstEthToken, address(alice), amount2);
        wstEthToken.approve(address(borrowLend.aavePool()), amount2);
        borrowLend.aavePool().supply(address(wstEthToken), amount2, address(borrowLend), 0);
        vm.stopPrank();

        assertEq(borrowLend.aaveAToken().scaledBalanceOf(address(borrowLend)), B + A);

        console.log("Total scaledBalance          ====>   ", borrowLend.aaveAToken().scaledBalanceOf(address(borrowLend)));
        console.log("Total Balance                ====>   ", borrowLend.aaveAToken().balanceOf(address(borrowLend)));
        
        uint256 recoverTokenAmount = IERC20(SPARK_WSTETH_A_TOKEN).balanceOf(address(borrowLend)) - borrowLend.suppliedBalance();
        
        console.log("The donated token amount     ====>   ", amount2);
        console.log("The clamiable token amount   ====>   ", recoverTokenAmount);

        vm.startPrank(origamiMultisig);
        borrowLend.recoverToken(SPARK_WSTETH_A_TOKEN, bob, recoverTokenAmount);

        console.log("Current balance              ====>   ", borrowLend.aaveAToken().balanceOf(address(borrowLend)));
        console.log("The tracked suppliedBalance  ====>   ", borrowLend.suppliedBalance());

        assertGt(borrowLend.suppliedBalance(), borrowLend.aaveAToken().balanceOf(address(borrowLend)));
}
```

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
The following fix will be safe and sufficient.
```
function recoverToken(address token, address to, uint256 amount) external onlyElevatedAccess {       
    // If the token to recover is the aaveAtoken, can only remove any *surplus* reserves (ie donation reserves).
    // It can't dip into the actual user added reserves. 
    if (token == address(aaveAToken)) {
        uint256 bal = aaveAToken.balanceOf(address(this));
        if (amount > (bal - suppliedBalance())) revert CommonEventsAndErrors.InvalidAmount(token, amount);
    }

    emit CommonEventsAndErrors.TokenRecovered(to, token, amount);
    IERC20(token).safeTransfer(to, amount);

+     if (token == address(aaveAToken) && _aTokenShares > aaveAToken.scaledBalanceOf(address(this))) {
+         _aTokenShares = aaveAToken.scaledBalanceOf(address(this));
+     }
}
```
