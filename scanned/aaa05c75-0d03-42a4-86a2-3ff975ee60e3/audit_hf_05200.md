# [H] Minting in between disabling and re‑enabling burning leads to stuck funds and dilution of later burners

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23321
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Burning of child tokens can be disabled after `PaymentSettler::enableBurning` has been called by an admin calling `CentralToken::disableBurning` directly on the parent of the child tokens.  
However, an admin could call mint once `disableBurning` as called because of the following line in `mint`  

```solidity
function mint(address to, uint64 amount) external nonReentrant whenNotPaused restricted {
    if (amount == 0) return;
    @> if (mintDisabled || burnable()) revert MintDisabled();
    _checkAllowedAdmin(to);
    _mint(to, amount);
    preBurnSupply += amount;
    emit TokensMinted(to, amount);
}
```

There are two ways in which the burning can be resumed  

1. `PaymentSettler::enableBurning`  
2. `CentralToken::enableBurning`  

Both lead to funds being stuck in the `CentralToken` contract.

The problems with `PaymentSettler::enableBurning` are also covered in Issue After disabling burning with `CentralToken::disableBurning` calling `PaymentSettler::enableBurning` leads to stuck funds. However, we go through the specific case here:

**Case 1: PaymentSettler::enableBurning**  
We use specific values for clarity  

- Initial 10,000 CentralTokens are minted. `totalSupply == 10_000`. `preBurnSupply == 10_000`  
- `PaymentSettler::enableBurning(centralToken, fundingWallet, 1_000_000e6)` is called adding 1,000,000 USDC  
  – Let PaymentSettler's token data for the central token be `t`. Thus `t.balance = 1_000_000e6`  
  – Indirectly, this sets `CentralToken`'s `totalBurnPayout` storage variable to `1_000_000e6`  
- 5,000 of these are burned (at 100 USDC/token reducing) `t.balance` to `500_000e6` and reducing `totalSupply` to 5,000  
- Burning is disabled with `CentralToken.disableBurning()`  
- `CentralToken::mint` is called to mint an additional 6,000 tokens. `totalSupply = 11_000`  
  – However, `preBurnSupply` is increased to `16_000`  
- Now `PaymentSettler::enableBurning(centralToken, fundingWallet, 600_000e6)` is called  
  – `t.balance` is increased to `1_100_000e6`  
  – As described in Issue After disabling burning with `CentralToken::disableBurning` calling `PaymentSettler::enableBurning` leads to stuck funds this overwrites `totalBurnPayout` to `600_000e6`  
- Now there are  
  – 11,000 child tokens  
  – `preBurnSupply = 16_000`  
  – `t.balance = 1_100_000e6`  
  – `totalBurnPayout == 600_000e6`  

Each token can be redeemed for `totalBurnPayout / preBurnSupply` stable coins. This is `600_000e6 / 16_000 == 37.5e6`. They have been heavily diluted by the fact that `totalBurnPayout` was overridden.  

This reduces `t.balance` by `11_000 * 37.5e6 == 412_500e6` to `687_500e6`, which are now stuck funds.

**Case 2: CentralToken::enableBurning**  
This case is the same as before, up until the minting of the 5,000 new central tokens.  

But now:  

- `CentralToken::enableBurning` is called (which ignores the `burnPayout` parameter)  
- Now there are:  
  – 11,000 child tokens  
  – `preBurnSupply = 16_000`  
  – `t.balance = 500_000e6`  
  – `totalBurnPayout == 1_600_000e6`  

Now we calculate that each token can be redeemed for `1_000_000e6 / 16_000 == 62.5e6`.  

The total value of all the remaining child tokens is `11_000 * 62.5e6 == 687_500e6`.  

`t.balance` is not large enough to cover this so now some of the child token cannot even be burned.

This is bad enough but if we change the scenario slightly so that `t.balance` also includes dividends/rent from the property so that there is enough to cover the `687_500e6` required to burn the remaining child tokens, then by burning them one is actually stealing the dividends/rents that the burners of the first 5,000 tokens may not have claimed.

**Impact:**  
If burning is re‑enabled with `PaymentSettler::enableBurning` funds will (generally) become stuck.  
If burning is re‑enabled with `CentralToken::enableBurning`, in many cases, there will not be enough funds in the PaymentSettler contract to cover burning of all tokens. Further, if PaymentSettler contains payouts (in addition to the funds intended for burns) then burning could have the effect of stealing other users' unclaimed payouts.

## Proof of Concept
Add the following to `PaymentSettlerTest.t.sol`

```solidity
function test_cyfrin_MintBetweenDisableEnableBurn_Case1() public {
    address user0 = getDomesticUser(0);
    address user1 = getDomesticUser(1);
    centralTokenProxy.mint(address(this), uint64(10000));
    centralTokenProxy.dynamicTransfer(user0, 5000);
    centralTokenProxy.dynamicTransfer(user1, 5000);
    (uint128 usdBal0 , , bool burnEnabled0,) =
        paySettlerProxy.tokenData(address(centralTokenProxy));,!
    assertEq(usdBal0, 0);
    assertEq(burnEnabled0, false);
    // initiateBurning
    paySettlerProxy.initiateBurning(address(centralTokenProxy));
    skip(1 days + 1);
    uint64 burnFunds0 = 1_000_000e6; // first funding (USD6 units)
    IERC20(address(stableCoin)).approve(address(paySettlerProxy), type(uint256).max);
    paySettlerProxy.enableBurning(address(centralTokenProxy), address(this), burnFunds0);
    (uint128 usdBal1,,bool burnEnabled1,) = paySettlerProxy.tokenData(address(centralTokenProxy));
    assertEq(usdBal1, 1_000_000e6);
    assertEq(centralTokenProxy.totalSupply(), 10_000);
    assertEq(centralTokenProxy.preBurnSupply(), 10_000);
    assertEq(centralTokenProxy.totalBurnPayout(), 1_000_000e6);
    assertEq(burnEnabled1, true);
    vm.startPrank(user0);
    d_childTokenProxy.burn(); // burns 5000 tokens
    vm.stopPrank();
    (uint128 usdBal2,,,) = paySettlerProxy.tokenData(address(centralTokenProxy));
    assertEq(usdBal2, 500_000e6);
    assertEq(centralTokenProxy.totalSupply(), 5_000);
    assertEq(centralTokenProxy.preBurnSupply(), 10_000);
    assertEq(centralTokenProxy.totalBurnPayout(), 1_000_000e6);
    // Disable Burning
    centralTokenProxy.disableBurning();
    (,,bool burnEnabled2_5,) = paySettlerProxy.tokenData(address(centralTokenProxy));
    assertEq(burnEnabled2_5, true); // PaymentSettler still reports that the burn is enabled
    // Mint new tokens and distribute to user1
    centralTokenProxy.mint(address(this), 6_000);
    centralTokenProxy.dynamicTransfer(user1, 6_000);
    uint64 burnFunds1 = 600_000e6;
    paySettlerProxy.enableBurning(address(centralTokenProxy), address(this), burnFunds1);
    (uint128 usdBal3 , , , bool burnEnabled3) =
        paySettlerProxy.tokenData(address(centralTokenProxy));,!
    assertEq(usdBal3, 1_100_000e6);
    assertTrue(burnEnabled3);
    assertEq(centralTokenProxy.totalSupply(), 11_000);
    assertEq(centralTokenProxy.preBurnSupply(), 16_000);
    assertEq(centralTokenProxy.totalBurnPayout(), 600_000e6);
    vm.startPrank(user1);
    d_childTokenProxy.burn(); // burn all remaining tokens
    vm.stopPrank();
    (uint128 usdBalEnd , , , ) = paySettlerProxy.tokenData(address(centralTokenProxy));
    assertEq(usdBalEnd, 687_500e6);
    assertEq(centralTokenProxy.totalSupply(), 0);
}
function test_cyfrin_MintBetweenDisableEnableBurn_Case2() public {
    address user0 = getDomesticUser(0);
    address user1 = getDomesticUser(1);
    centralTokenProxy.mint(address(this), uint64(10000));
    centralTokenProxy.dynamicTransfer(user0, 5000);
    centralTokenProxy.dynamicTransfer(user1, 5000);
    (uint128 usdBal0 , , bool burnEnabled0,) =
        paySettlerProxy.tokenData(address(centralTokenProxy));,!
    assertEq(usdBal0, 0);
    assertEq(burnEnabled0, false);
    // initiateBurning
    paySettlerProxy.initiateBurning(address(centralTokenProxy));
    skip(1 days + 1);
    uint64 burnFunds0 = 1_000_000e6; // first funding (USD6 units)
    IERC20(address(stableCoin)).approve(address(paySettlerProxy), type(uint256).max);
    paySettlerProxy.enableBurning(address(centralTokenProxy), address(this), burnFunds0);
    (uint128 usdBal1,,bool burnEnabled1,) = paySettlerProxy.tokenData(address(centralTokenProxy));
    assertEq(usdBal1, 1_000_000e6);
    assertEq(centralTokenProxy.totalSupply(), 10_000);
    assertEq(centralTokenProxy.preBurnSupply(), 10_000);
    assertEq(centralTokenProxy.totalBurnPayout(), 1_000_000e6);
    assertEq(burnEnabled1, true);
    vm.startPrank(user0);
    d_childTokenProxy.burn(); // burns 5000 tokens
    vm.stopPrank();
    (uint128 usdBal2,,,) = paySettlerProxy.tokenData(address(centralTokenProxy));
    assertEq(usdBal2, 500_000e6);
    assertEq(centralTokenProxy.totalSupply(), 5_000);
    assertEq(centralTokenProxy.preBurnSupply(), 10_000);
    assertEq(centralTokenProxy.totalBurnPayout(), 1_000_000e6);
    // Disable Burning
    centralTokenProxy.disableBurning();
    (,,bool burnEnabled2_5,) = paySettlerProxy.tokenData(address(centralTokenProxy));
    assertEq(burnEnabled2_5, true); // PaymentSettler still reports that the burn is enabled
    // Mint new tokens and distribute to user1
    centralTokenProxy.mint(address(this), 6_000);
    centralTokenProxy.dynamicTransfer(user1, 6_000);
    centralTokenProxy.enableBurning(0); // burnPayout parameter ignored
    (uint128 usdBal3 , , , bool burnEnabled3) =
        paySettlerProxy.tokenData(address(centralTokenProxy));,!
    assertEq(usdBal3, 500_000e6);
    assertTrue(burnEnabled3);
    uint256 totalSupply3 = centralTokenProxy.totalSupply();
    uint64 preBurnSupply3 = centralTokenProxy.preBurnSupply();
    uint64 totalBurnPayout3 = centralTokenProxy.totalBurnPayout();
    uint256 valueOfTokens = totalSupply3 * totalBurnPayout3 / preBurnSupply3;
    assertEq(valueOfTokens, 687_500e6);
    assertGt(valueOfTokens, usdBal3);
    assertEq(totalSupply3, 11_000);
    assertEq(preBurnSupply3, 16_000);
    assertEq(totalBurnPayout3, 1_000_000e6);
    vm.startPrank(user1);
    vm.expectPartialRevert(bytes4(keccak256("InsufficientBalance(address)")));
    d_childTokenProxy.burn(); // burn all remaining tokens
    vm.stopPrank();
}
```

## Recommendation
Information not provided
