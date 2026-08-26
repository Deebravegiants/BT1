# [M] Return values of transfer()/transferFrom() not checked

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-20
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/381
Type: code-finding

## Details
### Lines of code

--------------

[377](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L377-L380), [509](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L509-L513), [491](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L491-L494), [530](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L530-L534), [42](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/LTap.sol#L42-L42), [50](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/LTap.sol#L50-L50)

### Vulnerability details

-------------

Not all `IERC20` implementations `revert()` when there's a failure in `transfer()`/`transferFrom()`. The function signature has a `boolean` return value and they indicate errors that way [instead](https://etherscan.io/address/0x25d772b21b0e5197f2dc8169e3aa976b16be04ac#code#F1#L44). By not checking the return value, operations that should have marked as failed, may potentially go through without actually making a payment

```solidity
File: contracts/option-airdrop/AirdropBroker.sol

377                  paymentToken.transfer(
378                      paymentTokenBeneficiary,
379                      paymentToken.balanceOf(address(this))
380:                 );

509          _paymentToken.transferFrom(
510              msg.sender,
511              address(this),
512              discountedPaymentAmount
513:         );

```



```solidity
File: contracts/options/TapiocaOptionBroker.sol

491                  paymentToken.transfer(
492                      paymentTokenBeneficiary,
493                      paymentToken.balanceOf(address(this))
494:                 );

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/381_
