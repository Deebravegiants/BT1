# [M] Unlimited type(uint256).max allowance approval has risk in TrueFiStrategy.sol

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L72
Type: audit-issue

## Details
# Unlimited type(uint256).max allowance approval has risk in TrueFiStrategy.sol

## Summary

in the constructor of the TrueFiStragety.sol

Unlimited type(uint256).max allowance is given to tfUSDC and tfFarm contract,

unlimited allowance is considered risky.

## Vulnerability Detail

In the construtor of the TrueFiStragety.sol

the code below given unlimited allowance spending limit to  tfUSDC and tfFarm contract,

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L72

```solidity
  constructor(IMaster _initialParent) BaseNode(_initialParent) {
    // Approve tfUSDC max amount of USDC
    want.safeIncreaseAllowance(address(tfUSDC), type(uint256).max);
    // Approve tfFarm max amount of tfUSDC
    tfUSDC.safeIncreaseAllowance(address(tfFarm), type(uint256).max);
  }
```

However,  setting unlimited allowance is considered risky because if underlying smart contract
is compromised, the contract can drain all the fund from the TrueFiStrategy.sol

the underlying smart contract tfUSDC and tfFram are proxy contracts and delegate to its implementation

tfFrame proxy below

https://etherscan.io/address/0xec6c3FD795D6e6f202825Ddb56E01b3c128b0b10#code

tfUSDC proxy below

https://etherscan.io/address/0xA991356d261fbaF194463aF6DF8f0464F8f1c742#code

If the underlying proxy contract's admin key is compromised, the hacker can upgrade the implementation contract to a malicious
contract and transfer all the fund from the TrueFiStragety.sol contract.

As shown in this article:

Unlimited ERC20 allowances considered harmful

I want to quote

As we know, bugs can exist and exploits can happen even in established projects. 
And by giving these platforms an unlimited allowance, you do not only expose your deposited 
funds to these risks, but also the tokens that you're holding "safely" in your wallet.

![image](https://user-images.githubusercontent.com/114844362/193451149-4f45905c-7a53-41cc-aee3-fc27ba16a2ff.png)


https://kalis.me/unlimited-erc20-allowances/

## Impact

if underlying smart contract that have unlimited allowance is compromised, the contract can drain all the fund from the TrueFiStragety.sol and result in user fund loss.

## Code Snippet

## Tool used

Manual Review

## Recommendation

I also want to quote from this article

https://kalis.me/unlimited-erc20-allowances/

The most practical of those solutions is using the approve-spend pattern. 

In this pattern you only request the user to approve the exact amount that they want to use at that moment, 

rather than an unlimited amount.

Instead of giving max allowance in the constructor, we can implement this pattern below

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/TrueFiStrategy.sol#L88

```solidity
  function _deposit() internal override whenNotPaused {
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueFiPool2.sol#L469
    uint256 wantTokenBalance = want.balanceOf(address(this));
    want.safeIncreaseAllowance(address(tfUSDC), wantTokenBalance);
    tfUSDC.join(wantTokenBalance);

    // Don't stake in the tfFarm if shares are 0
    // This would make the function call revert
    // https://github.com/trusttoken/contracts-pre22/blob/main/contracts/truefi2/TrueMultiFarm.sol#L101
    if (tfFarm.getShare(tfUSDC) == 0) return;

    // How much tfUSDC is in this contract
    // Could both be tfUSDC that was already in here before the `_deposit()` call
    // And new tfUSDC that was minted in the `tfUSDC.join()` call
    uint256 tfUsdcBalance = tfUSDC.balanceOf(address(this));

    // Stake all tfUSDC in the tfFarm
    tfUSDC.safeIncreaseAllowance(address(tfFarm), tfUsdcBalance);
    tfFarm.stake(tfUSDC, tfUsdcBalance);
  }
```
