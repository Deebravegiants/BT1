# [M] Possible Dos Of Withdraw Due To Grosss Amount For Net Calculation In `DStakeToken::previewWithdraw()`

## Summary
Severity: Medium
Chain: Smart contract
Component: dTRINITY
Published: 2025-06-27
Source: https://github.com/hats-finance/dTRINITY-0xee5c6f15e8d0b55a5eff84bb66beeee0e6140ffe/issues/273
Type: hats-finding

## Details
**Github username:** @OxTheAnzRider
  **Twitter username:** --
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/0xtheanzrider)

  **Beneficiary:** 0xF78554Dfb77e2Da05BAeE87913CA9706eD40a027
  **Submission hash (on-chain):** 0x2c25aeb47be52c870cd674f110a1d400b501d50c7dc68b8f2d22b6149929c04d
  **Severity:** medium
  
  **Description:**
  **Description**

On withdraw the function follows a logic where it uses the asset amount as an input to call the `previewWithdraw()` to calculate the amount of share but then uses the share as an input calling the `convertToAssets()` to get the gross amount then does a check to ensure the gross amount is less or equal to the maxwithdraw of the user(owner)
```solidity
    function withdraw(
        uint256 assets,
        address receiver,
        address owner
    ) public virtual override returns (uint256 shares) {
        shares = previewWithdraw(assets); // Calculate shares needed for net amount
        uint256 grossAssets = convertToAssets(shares); // Calculate gross amount from shares

        require(
            grossAssets <= maxWithdraw(owner),
            "ERC4626: withdraw more than max"
        );

        _withdraw(_msgSender(), receiver, owner, grossAssets, shares); // Pass GROSS amount to _withdraw
        return shares;
    }
```
the `previewWithdraw()` uses `_getGrossAmountRequiredForNet()` to get the the gross amount for net  then uses it to calculate the amount of of shares used for the gross amount calculation in the `withdraw()`. And if fee is set `_getGrossAmountRequiredForNet()` uses the formula
```solidity
        // grossAmount = netAmount / (1 - feeBps/ONE_HUNDRED_PERCENT_BPS)
        // grossAmount = netAmount * ONE_HUNDRED_PERCENT_BPS / (ONE_HUNDRED_PERCENT_BPS - feeBps)
        return
            (netAmount * BasisPointConstants.ONE_HUNDRED_PERCENT_BPS) /
            (BasisPointConstants.ONE_HUNDRED_PERCENT_BPS - withdrawalFeeBps_);
 ```   
But this calculation in most situation lead the gross amount to being more than the maxwithdraw causing a revert.
```solidity
        require(
            grossAssets <= maxWithdraw(owner),
            "ERC4626: withdraw more than max"
        );
 ``` 
 **Details**
- say a user deposited 1000asset token and got 1000share tokens
- on call to withdraw the entire asset token when `previewWithdraw()::_getGrossAmountRequiredForNet` function
```
grossAssetsRequired: 1000*1000000/1000000-10000) //assuming the fee is set to the Max feeBP
= 1010
```

which is then used to get 1010share tokens which is used to calculate gross amount which leads to 1010asset causing it to be greater than the max withdraw(1000 asset)

the following below is the calculation for easy comprehension
```solidity
   function previewWithdraw(uint256 assets) public view virtual returns (uint256) {
        return _convertToShares(assets, Math.Rounding.Ceil);
    }
      function _convertToShares(uint256 assets, Math.Rounding rounding) internal view virtual returns (uint256) {
        return assets.mulDiv(totalSupply() + 10 ** _decimalsOffset(), totalAssets() + 1, rounding);
    }
```
   assuming total supply = 1000;

   and total asset = 1000;

    super.previewWithdraw:
    1010*1000+1/1000+1 = 1010shares
    
```solidity    
       function convertToAssets(uint256 shares) public view virtual returns (uint256) {
        return _convertToAssets(shares, Math.Rounding.Floor);
    }

    function _convertToAssets(uint256 shares, Math.Rounding rounding) internal view virtual returns (uint256) {
        return shares.mulDiv(totalAssets() + 1, totalSupply() + 10 ** _decimalsOffset(), rounding);
    }
```
    grossamount:
    1010*1000+1/1000+1 = 1010asset
    
    so: 1010 > maxwithdraw(1000Asset)
    
**ADITIONAL**

why this wasn't caught in the DstakeToken.ts test was because the grossamount was calculated outside and used as the input to mint
```solidity
        await DStakeToken.connect(user1).setWithdrawalFee(10000);

        // Calculate the correct gross deposit amount needed to have enough shares
        // to withdraw 100 assets net. We need to deposit enough so that after
        // fees are deducted, we can still withdraw 100 assets.
        //
        // For mathematical correctness:
        // grossAmount = netAmount * ONE_HUNDRED_PERCENT_BPS / (ONE_HUNDRED_PERCENT_BPS - feeBps)
        // grossAmount = 100 * 1000000 / (1000000 - 10000) = 100 * 1000000 / 990000
        const grossDeposit = (assetsToDeposit * 1000000n) / (1000000n - 10000n);

        await stable.mint(user1.address, grossDeposit);
        await dStableToken
          .connect(user1)
          .approve(DStakeTokenAddress, grossDeposit);
        shares = await DStakeToken.previewDeposit(grossDeposit);
        await DStakeToken.connect(user1).deposit(grossDeposit, user1.address);
      });
 ```
 
 so if the `assetsToDeposit`  was 100 due to the gross amount calculation the input for mint became 101 and produced 101shares
 
 and on withdraw the assetToDeposit was used as the withdrawal input so the check for 
 ```solidity
        require(
            grossAssets <= maxWithdraw(owner),
            "ERC4626: withdraw more than max"
        );
```
passed to withdraw 100assets tokens as the maxwithdraw was 101tokens.

```solidity

      it("should withdraw assets with fee deducted", async () => {
        // When we call withdraw(100), the user wants 100 net assets
        // The contract calculates the gross amount needed and takes a fee from that
        const grossAmountNeeded =
          (assetsToDeposit * 1000000n) / (1000000n - 10000n);
        const fee = (grossAmountNeeded * 10000n) / 1000000n;
        // The user should receive exactly the amount they requested (100 assets)
        const netAssets = assetsToDeposit; // This should be exactly 100

        await expect(
          DStakeToken.connect(user1).withdraw(
            assetsToDeposit, //@audit
            user1.address,
            user1.address
          )
        )
          .to.emit(DStakeToken, "WithdrawalFee")
          .withArgs(user1.address, user1.address, fee);
        expect(await dStableToken.balanceOf(user1.address)).to.equal(netAssets);
        expect(await DStakeToken.balanceOf(user1.address)).to.equal(0n);
      });
 ```     
**Note**: Another thing to note is that the withdraw logic(that's is the grossamount calculation in `preveiwWithdraw` forces users to not be able to withdraw all there tokens as if the  share token were say a `1000` the grossamount  calculated will lead to an accounting problem where the calculated is about `1010`, more than the users maxWithdraw leading to user having to reconfigure there input to be able to withdraw 1000assets but have some share tokens left.

But the major **impact** of this is incorrect accounting as the users can still configure there asset amount to be able to withdraw their initial asset token(if the have the knowledge of how the accounting of the protocol works but i highly doubt) . The definition of the severity of this issue to the judge and protocol team to decide but upto me this is a meduim but can be argued as a low depending. Also if this is a design; it lead lead to user side confusion and panick

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

2. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
