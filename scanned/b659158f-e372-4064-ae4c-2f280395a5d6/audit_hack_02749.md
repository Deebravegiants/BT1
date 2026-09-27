# [M] Unlimited type(uint256).max allowance approval has risk in EulerStragety.sol

## Summary
Severity: Medium
Reporter: ctf_sec
Source: https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L31
Type: audit-issue

## Details
# Unlimited type(uint256).max allowance approval has risk in EulerStragety.sol

## Summary

in the constructor of the EulerStragety.sol,

Unlimited type(uint256).max allowance is given to EULER contract,

unlimited allowance is considered risky.

## Vulnerability Detail

In the construtor of the EulerStragety.sol

the code below given unlimited allowance spending limit to EULER contract

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L31

```solidity
  /// @param _initialParent Contract that will be the parent in the tree structure
  constructor(IMaster _initialParent) BaseNode(_initialParent) {
    // Approve Euler max amount of USDC
    want.safeIncreaseAllowance(EULER, type(uint256).max);
  }
```

However,  setting unlimited allowance is considered risky because if underlying smart contract
is compromised, the contract can drain all the fund into the EulerStragety.sol

the underlying smart contract Euler is a proxy contract and delegate to its implementation

https://etherscan.io/address/0x27182842E098f60e3D576794A5bFFb0777E025d3#code

If the underlying proxy contract's admin key is compromised, the hacker can upgrade the implementation contract to a malicious
contract and transfer all the fund from the EulerStragety.sol contract.

As shown in this article:

Unlimited ERC20 allowances considered harmful

I want to quote

As we know, bugs can exist and exploits can happen even in established projects. 
And by giving these platforms an unlimited allowance, you do not only expose your deposited 
funds to these risks, but also the tokens that you're holding "safely" in your wallet.

![image](https://user-images.githubusercontent.com/114844362/193451149-4f45905c-7a53-41cc-aee3-fc27ba16a2ff.png)


https://kalis.me/unlimited-erc20-allowances/

## Impact

if underlying smart contract that have unlimited allowance is compromised, the contract can drain all the fund from the EulerStragety.sol and result in user fund loss.

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

https://github.com/sherlock-audit/2022-09-sherlock/blob/main/sherlock-v2-core/contracts/strategy/EulerStrategy.sol#L51

```solidity
  /// @notice Deposit all USDC in this contract in Euler
  /// @notice Works under the assumption this contract contains USDC
  function _deposit() internal override whenNotPaused {
    uint256 balance = IERC20(want).balanceOf(this);
    want.safeIncreaseAllowance(EULER, balanceEuler);
    EUSDC.deposit(SUB_ACCOUNT, type(uint256).max);
  }
```
