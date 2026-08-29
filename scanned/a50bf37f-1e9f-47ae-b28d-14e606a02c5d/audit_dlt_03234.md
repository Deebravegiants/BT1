# [M] Contracts are vulnerable to fee-on-transfer accounting-related issues

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-20
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/389
Type: code-finding

## Details
### Lines of code

--------------

[359](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/BaseTOFT.sol#L359-L359), [448](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L448-L448), [509](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L509-L513), [530](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L530-L534), [42](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/LTap.sol#L42-L42), [797](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L797-L797), [162](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/BaseSwapper.sol#L162-L162)

### Vulnerability details

-------------

The functions below transfer funds from the caller to the receiver via `transferFrom()`, but do not ensure that the actual number of tokens received is the same as the input amount to the transfer. If the token is a fee-on-transfer token, the balance after the transfer will be smaller than expected, leading to accounting issues. Even if there are checks later, related to a secondary transfer, an attacker may be able to use latent funds (e.g. mistakenly sent by another user) in order to get a free credit. One way to solve this problem is to measure the balance before and after the transfer, and use the difference as the amount, rather than the stated amount.

```solidity
File: contracts/tOFT/BaseTOFT.sol

359:         IERC20(erc20).safeTransferFrom(_fromAddress, address(this), _amount);

```



```solidity
File: contracts/governance/twTAP.sol

448:         rewardToken.safeTransferFrom(msg.sender, address(this), _amount);

```



```solidity
File: contracts/option-airdrop/AirdropBroker.sol

509          _paymentToken.transferFrom(
510              msg.sender,
511              address(this),
512              discountedPaymentAmount
513:         );
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/389_
