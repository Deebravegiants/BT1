# [M] \[M01\] `ERC20` transfers can misbehave

## Summary
Severity: Medium
Source: https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L1071
Type: audit-issue

## Details
The [\_transferFromERC20](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L1071) function is used throughout `ACOToken.sol` to handle transferring funds into the contract from a user. It is called [within mint](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L403), [within mintTo](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L418), and [within \_validateAndBurn](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L750). In each case, the destination is the `ACOToken` contract.

Such transfers may behave unexpectedly if the token contract charges fees. As an example, the popular USDT token does not presently charge any fees upon transfer, but it has the potential to do so. In this case the amount received would be less than the amount sent. Such tokens have the potential to lead to protocol insolvency when they are used to mint new `ACOToken`s.

Transfers may also behave unexpectedly when they don’t `throw` upon an execution’s failure. Remember that the [ERC20 standard](https://eips.ethereum.org/EIPS/eip-20) allows for such tokens to still be considered `ERC20` compliant. In this case, the [require on line 1073](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L1073) or [line 1061](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L1061) may not cause a `revert`, since `success` will be true.

In the case of [\_transferERC20](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L1059), similar issues can occur, and could cause users to receive less than expected [when collateral is transferred](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L624) or [when exercise assets are transferred](https://github.com/AuctusProject/aco/blob/36bcab024c9781d799381f8f973e99fd5b0f4d2d/smart-contracts/contracts/core/ACOToken.sol#L720).

Consider thoroughly vetting each token used within an ACO options pair, ensuring that failing `transferFrom` and `transfer` calls will cause reverts within `ACOToken.sol`. Additionally, consider implementing some sort of sanity check which enforces that the balance of the `ACOToken` contract increases by the desired amount when calling `_transferFromERC20`. See related issue [**Warning about listing tokens**](#l07).

**Update:** _Ackowledged. Auctus’ statement for this issue:_

> The team is aware and will always check if new token pairs are supported, paying attention to the points mentioned in \[L07\]
