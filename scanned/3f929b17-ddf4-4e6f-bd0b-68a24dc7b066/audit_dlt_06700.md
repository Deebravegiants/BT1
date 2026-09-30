# [H] Attacker can manipulate the system to trigger Increase leverage and prevent users from ever withdrawing

## Summary
Severity: High
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-18
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/119
Type: hats-finding

## Details
**Github username:** @Tomiwasa0
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Bigsam)

  **Beneficiary:** 0x95f04DaAf8999F9fD232eB61916952Da2CE197A8
  **Submission hash (on-chain):** 0x0f74d6c2215c759ff2f7356e64263f81547b0c7f5c10047db8de44b0cd49d4f6
  **Severity:** high
  
  **Description:**
  **Description**\

The attacker can manipulate the Share to Asset calculation, which in turn affects the increase/ decrease leverage functions, permanent DOS and also DOS withdrawal for all other users. 

The total Asset function causes this issue. 

The total asset is obtained by calling the get user's details But this function calculates all the positional balances of a user.
While total debt can not be manipulated, Total Collateral can be. 

```solidity

 /**
     * @dev Override of totalAssets from ERC4626
     * @return uint256 Total assets in the vault
     */
    function totalAssets() public view virtual override returns (uint256) {
        // We override this function to return the total assets in the vault
        // with respect to the position in the lending pool
        // The dLend interest will be distributed to the dToken
        (uint256 totalCollateralBase, ) = getTotalCollateralAndDebtOfUserInBase(
            address(this)
        );
        // The price decimals is cancelled out in the division (as the amount and price are in the same unit)
        return
            convertFromBaseCurrencyToToken(
                totalCollateralBase,
                address(collateralToken)
            );
    }

```


```solidity
  function calculateUserAccountData(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    mapping(uint8 => DataTypes.EModeCategory) storage eModeCategories,
    DataTypes.CalculateUserAccountDataParams memory params
  ) internal view returns (uint256, uint256, uint256, uint256, uint256, bool) {
    if (params.userConfig.isEmpty()) {
      return (0, 0, 0, 0, type(uint256).max, false);
    }

    CalculateUserAccountDataVars memory vars;

    if (params.userEModeCategory != 0) {
      (vars.eModeLtv, vars.eModeLiqThreshold, vars.eModeAssetPrice) = EModeLogic
        .getEModeConfiguration(
          eModeCategories[params.userEModeCategory],
          IPriceOracleGetter(params.oracle)
        );
    }

    while (vars.i < params.reservesCount) {
      if (!params.userConfig.isUsingAsCollateralOrBorrowing(vars.i)) {
        unchecked {
          ++vars.i;
        }
        continue;
      }

      vars.currentReserveAddress = reservesList[vars.i];

      if (vars.currentReserveAddress == address(0)) {
        unchecked {
          ++vars.i;
        }
        continue;
      }

      DataTypes.ReserveData storage currentReserve = reservesData[vars.currentReserveAddress];

      (
        vars.ltv,
        vars.liquidationThreshold,
        ,
        vars.decimals,
        ,
        vars.eModeAssetCategory
      ) = currentReserve.configuration.getParams();

      unchecked {
        vars.assetUnit = 10 ** vars.decimals;
      }

      vars.assetPrice = vars.eModeAssetPrice != 0 &&
        params.userEModeCategory == vars.eModeAssetCategory
        ? vars.eModeAssetPrice
        : IPriceOracleGetter(params.oracle).getAssetPrice(vars.currentReserveAddress);

      if (vars.liquidationThreshold != 0 && params.userConfig.isUsingAsCollateral(vars.i)) {
        vars.userBalanceInBaseCurrency = _getUserBalanceInBaseCurrency(
          params.user,
          currentReserve,
          vars.assetPrice,
          vars.assetUnit
        );

        vars.totalCollateralInBaseCurrency += vars.userBalanceInBaseCurrency;

        vars.isInEModeCategory = EModeLogic.isInEModeCategory(
          params.userEModeCategory,
          vars.eModeAssetCategory
        );

        if (vars.ltv != 0) {
          vars.avgLtv +=
            vars.userBalanceInBaseCurrency *
            (vars.isInEModeCategory ? vars.eModeLtv : vars.ltv);
        } else {
          vars.hasZeroLtvCollateral = true;
        }

        vars.avgLiquidationThreshold +=
          vars.userBalanceInBaseCurrency *
          (vars.isInEModeCategory ? vars.eModeLiqThreshold : vars.liquidationThreshold);
      }

      if (params.userConfig.isBorrowing(vars.i)) {
        vars.totalDebtInBaseCurrency += _getUserDebtInBaseCurrency(
          params.user,
          currentReserve,
          vars.assetPrice,
          vars.assetUnit
        );
      }

      unchecked {
        ++vars.i;
      }
    }

    unchecked {
      vars.avgLtv = vars.totalCollateralInBaseCurrency != 0
        ? vars.avgLtv / vars.totalCollateralInBaseCurrency
        : 0;
      vars.avgLiquidationThreshold = vars.totalCollateralInBaseCurrency != 0
        ? vars.avgLiquidationThreshold / vars.totalCollateralInBaseCurrency
        : 0;
    }

    vars.healthFactor = (vars.totalDebtInBaseCurrency == 0)
      ? type(uint256).max
      : (vars.totalCollateralInBaseCurrency.percentMul(vars.avgLiquidationThreshold)).wadDiv(
        vars.totalDebtInBaseCurrency
      );
    return (
      vars.totalCollateralInBaseCurrency,
      vars.totalDebtInBaseCurrency,
      vars.avgLtv,
      vars.avgLiquidationThreshold,
      vars.healthFactor,
      vars.hasZeroLtvCollateral
    );
  }

```






From the Dloopcorebase

GETTOTALCOLLATERALANDDEBTOFUSERINBASE returns the max collateral and max debt of address this not just the IMMUTABLE COLLATERAL ASSET SUPPLIED.



```solidity
  /* Constants */

    uint32 public immutable targetLeverageBps; // ie. 30000 = 300% in basis points, means 3x leverage
    ERC20 public immutable collateralToken;
    ERC20 public immutable debtToken;

    uint256 public constant BALANCE_DIFF_TOLERANCE = 1;

    /* Errors */

```

The contract address is built to allow just one asset, collateral token which is immutable.

Attack can use this to switch the collateral token Valuation from Usdc to Usdc plus WETH.


Attacker will call supply directly of the Aave fork, supply a different collateral which can be the debt token or any other token on behalf of the vault ( address(this)).

This donation will inflate the Total Collateral In Base reflecting now USDC the true collateral plus E.g WETH the donated token.

SInce this will cause the system to be imbalance 

Attacker will balance the system by calling 

```solidity


  /**
     * @dev Increases the leverage of the user by supplying collateral token and borrowing more debt token
     *      - It requires to spend the collateral token from the user's wallet to supply to the pool
     *      - It will send the borrowed debt token to the user's wallet
     * @param additionalCollateralTokenAmount The additional amount of collateral token to supply
     * @param minReceivedDebtTokenAmount The minimum amount of debt token to receive
     */
    function increaseLeverage(
        uint256 additionalCollateralTokenAmount,
        uint256 minReceivedDebtTokenAmount
    ) public nonReentrant {   (
            uint256 totalCollateralBase,
            uint256 totalDebtBase
        ) = getTotalCollateralAndDebtOfUserInBase(address(this));
        uint256 subsidyBps = getCurrentSubsidyBps();

        // Make sure only increase the leverage if it is below the target leverage
        uint256 currentLeverageBps = getCurrentLeverageBps();
        if (currentLeverageBps >= targetLeverageBps) {
            revert LeverageExceedsTarget(currentLeverageBps, targetLeverageBps);
        }

        // Need to calculate the required collateral token amount before transferring the additional collateral token
        // to the vault as it will change the current collateral token balance in the vault
        uint256 requiredCollateralTokenAmount = _getRequiredCollateralTokenAmountToRebalance(
                targetLeverageBps,
                totalCollateralBase,
                totalDebtBase,
                subsidyBps,
                additionalCollateralTokenAmount
            );

        // Only transfer the collateral token if there is an additional amount to supply
        if (additionalCollateralTokenAmount > 0) {
            // Transfer the additional collateral token from the caller to the vault
            collateralToken.safeTransferFrom(
                msg.sender,
                address(this),
                additionalCollateralTokenAmount
            );
        }

        // Calculate the amount of collateral token in base currency
        uint256 requiredCollateralTokenAmountInBase = convertFromTokenAmountToBaseCurrency(
                requiredCollateralTokenAmount,
                address(collateralToken)
            );

        // The amount of debt token to borrow (in base currency) is equal to the amount of collateral token supplied
        // plus the subsidy (bonus for the caller)
        uint256 borrowedDebtTokenInBase = (requiredCollateralTokenAmountInBase *
            (BasisPointConstants.ONE_HUNDRED_PERCENT_BPS + subsidyBps)) /
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS;

        // Calculate the new leverage after increasing the leverage
        uint256 newLeverageBps = ((totalCollateralBase +
            requiredCollateralTokenAmountInBase) *
            BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
            (totalCollateralBase +
                requiredCollateralTokenAmountInBase -
                totalDebtBase -
                borrowedDebtTokenInBase);

        // Make sure the new leverage is increasing and does not exceed the target leverage
        if (
            newLeverageBps > targetLeverageBps ||
            newLeverageBps <= currentLeverageBps
        ) {
            revert IncreaseLeverageOutOfRange(
                newLeverageBps,
                targetLeverageBps,
                currentLeverageBps
            );
        }

        // Supply the collateral token to the lending pool
        _supplyToPool(
            address(collateralToken),
            requiredCollateralTokenAmount,
            address(this)
        );

        // Borrow debt token
        uint256 borrowedDebtTokenAmount = convertFromBaseCurrencyToToken(
            borrowedDebtTokenInBase,
            address(debtToken)
        );

        // Slippage protection, to make sure the user receives at least minReceivedDebtTokenAmount
        if (borrowedDebtTokenAmount < minReceivedDebtTokenAmount) {
            revert RebalanceReceiveLessThanMinAmount(
                "increaseLeverage",
                borrowedDebtTokenAmount,
                minReceivedDebtTokenAmount
            );
        }

        // At this step, the _borrowFromPool wrapper function will also assert that
        // the borrowed amount is exactly the amount requested, thus we can safely
        // have the slippage check before calling this function
        _borrowFromPool(
            address(debtToken),
            borrowedDebtTokenAmount,
            address(this)
        );

        // Transfer the debt token to the user
        debtToken.safeTransfer(msg.sender, borrowedDebtTokenAmount);
    }

```



Increase leverage will allow the attacker to increase the debt token to match the total collateral in Base


Note collateral is now a combination of 2 Atokens of different tokens, donation and actual true collateral.


The attacker gets back the debt token which will act as his profit for rebalancing the pool.


Attacker can perform this over and over again creating a Collateral Balance that show 60% WETH and 40% USDC for examle


$18000 WETH and $ 12000

using the get leverage calculation

The leverage position will now have a debt of $20000.

 
1. WITHDRAW

When users want to withdraw they will pay debt token to claim their USDC.
BASED on the shares to asset calculation, 

E.G USER A owns 80% of the liquidity 

that is $24000

When he calls to withdraw $24000 of USDC his call to withdraw will revert because the actual USDC supply of the vault is $12000 and WETH which was used to rebalance the vault by the attacker can never be claimed by anyone. locking out users with $18000 worth of shares that will never be claimed.

```solidity

  function _withdraw(
        address caller,
        address receiver,
        address owner,
        uint256 assets,
        uint256 shares
    ) internal override nonReentrant {

  if (owner != caller) {
            _spendAllowance(owner, caller, shares);
        }

        // Check user's balance before burning shares
        uint256 userShares = balanceOf(owner);
        if (userShares < shares) {
            revert InsufficientShareBalanceToRedeem(owner, shares, userShares);
        }

        // Burn the shares
        _burn(owner, shares);

        // Make sure the current leverage is within the target range
        if (isTooImbalanced()) {
            revert TooImbalanced(
                getCurrentLeverageBps(),
                lowerBoundTargetLeverageBps,
                upperBoundTargetLeverageBps
            );
        }

        // Withdraw the collateral from the lending pool
        // After this step, the _withdrawFromPool wrapper function will also assert that
        // the withdrawn amount is exactly the amount requested.
        _withdrawFromPoolImplementation(caller, assets);

```


2. Decrease leverage 


Increase and decrease leverage also works based on the principle of withdrawing collateral asset which is hardcoded and immutable. hence eventually when the systemhits Increase leverage over and over again which is more likely because Interest rate for borrowing are based on COMPOUND interest in Aave while liquidity are based on Simple interest.


Constant decrease leverage call will cause Collateral asset USDC to reduce to a point where only WETH is available, hence all calls to maintain the system will revert.

Also in this state deposit will and withdraw will not work cause the system is in an imbalanced state.


Meaning no one can act till the position gets liquidated. Note 50% liquidation is possible on aave 

Which will create another opportunity for the attacker to more in and use the vault asset to rebalance the vault.  


**Attack Scenario**\

1. **Step 1: Supply Malicious Collateral**

* Attacker calls Aave's `supply(WETH, amount, vaultAddress)`.

2. **Step 2: Inflate Total Collateral**

* Vault reads inflated `getTotalCollateralAndDebtOfUserInBase(address(this))`.
* `totalAssets()` rises.

3. **Step 3: Call `increaseLeverage()`**

* Vault calculates leverage based on inflated base.
* Borrowed debt token is returned to the attacker.

4. **Step 4: Repeat**

* Perform this repeatedly until:

He reditributes the collateral asset from the actual USDC to USDC lus WETH, he doesn't even need to donate much as if the vault has a higher interet rate the different in keeps growing.


**Attachments**

1. **Proof of Concept (PoC) File**


1. Deploy vault contract.
2. Supply `collateralToken` (e.g. USDC) to initialize.
3. As attacker:

```solidity
aavePool.supply(WETH, 10 ether, address(vault));
```
4. Observe:

* `vault.totalAssets()` is inflated.
* `increaseLeverage()` allows more debt to be drawn.
* Users can no longer withdraw their USDC.

2. **Revised Code File (Optional)**

Fix is to query the Atoken balance of vault for the collateral asset alone and use that ha the total asset and not user get user data to obtain the total asset.


 ```solidity
  /**
     * @notice Returns the total assets managed by the vault.
     */
    function totalAssets() public view override returns (uint256) {
       
         // get the atoken address of the collateral token and query the actual total asset directly from there
 
        return $.aToken.balanceOf(address(this));
    }
```
