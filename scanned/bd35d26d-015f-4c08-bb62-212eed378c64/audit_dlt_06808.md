# [M] Inflation attack in VotiumStrategy

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-09-asymmetry
Published: 2023-09-27
Source: https://github.com/code-423n4/2023-09-asymmetry-findings/issues/35
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-09-asymmetry/blob/main/contracts/strategies/votium/VotiumStrategy.sol#L39


# Vulnerability details

## Summary

The VotiumStrategy contract is susceptible to the [Inflation Attack](https://mixbytes.io/blog/overview-of-the-inflation-attack), in which the first depositor can be front-runned by an attacker to steal their deposit.

## Impact

Both AfEth and VotiumStrategy acts as vaults: accounts deposit some tokens and get back another token (share) that represents their participation in the vault.

These types of contracts are potentially vulnerable to the inflation attack: an attacker can front-run the initial deposit to the vault to inflate the value of a share and render the front-runned deposit worthless. 

In AfEth, this is successfully mitigated by the slippage control. Any attack that inflates the value of a share to decrease the number of minted shares is rejected due to the validation of minimum output:

https://github.com/code-423n4/2023-09-asymmetry/blob/main/contracts/AfEth.sol#L166-L167

```solidity
166:         uint256 amountToMint = totalValue / priceBeforeDeposit;
167:         if (amountToMint < _minout) revert BelowMinOut();
```

However, this is not the case of VotiumStrategy. In this contract, no validation is done in the number of minted tokens. This means that an attacker can execute the attack by front-running the initial deposit, which may be from AfEth or from any other account that interacts with the contract. See _Proof of Concept_ for a detailed walkthrough of the issue.

https://github.com/code-423n4/2023-09-asymmetry/blob/main/contracts/strategies/votium/VotiumStrategy.sol#L39-L46

```solidity
39:     function deposit() public payable override returns (uint256 mintAmount) {
40:         uint256 priceBefore = cvxPerVotium();
41:         uint256 cvxAmount = buyCvx(msg.value);
42:         IERC20(CVX_ADDRESS).approve(VLCVX_ADDRESS, cvxAmount);
43:         ILockedCvx(VLCVX_ADDRESS).lock(address(this), cvxAmount, 0);
44:         mintAmount = ((cvxAmount * 1e18) / priceBefore);
45:         _mint(msg.sender, mintAmount);
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-09-asymmetry-findings/issues/35_
