# [H] depositAndAllocateForPartyB is broken due to

## Summary
Severity: High
Contest weight: 0.8972
Dataset id: 20164
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to incorrect precision, any users or external protocols utilizing the depositAndAllocateForPartyB to allocate 1000 USDC will end up only having 0.000000001 USDC allocated to their account. This might potentially lead to unexpected loss of funds due to the broken functionality if they rely on the accuracy of the function outcome to perform certain actions that deal with funds/assets.
The input amount of the depositForPartyB function must be in native precision (e.g. USDC should be 6 decimals) as the function will automatically scale the amount 18 precision in Lines 114-115 below.
ontracts/facets/Account/AccountFacetImpl.sol#L108
File: AccountFacetImpl.sol
```solidity
function depositForPartyB(uint256 amount) internal {
    IERC20(GlobalAppStorage.layout().collateral).safeTransferFrom(
        msg.sender,
        address(this),
        amount
    );
    uint256 amountWith18Decimals = (amount * 1e18) /
        (10 ** IERC20Metadata(GlobalAppStorage.layout().collateral).decimals());
    AccountStorage.layout().balances[msg.sender] += amountWith18Decimals;
}
```
On the other hand, the input amount of allocateForPartyB function must be in 18 decimals precision. Within the protocol, it uses 18 decimals for internal accounting.
ontracts/facets/Account/AccountFacetImpl.sol#L119
File: AccountFacetImpl.sol
```solidity
function allocateForPartyB(uint256 amount, address partyA, bool increaseNonce) internal {
    AccountStorage.Layout storage accountLayout = AccountStorage.layout();
    require(accountLayout.balances[msg.sender] >= amount, "PartyBFacet: Insufficient balance");
    require(
        !MAStorage.layout().partyBLiquidationStatus[msg.sender][partyA],
        "PartyBFacet: PartyB isn't solvent"
    );
    if (increaseNonce) {
        accountLayout.partyBNonces[msg.sender][partyA] += 1;
    }
    accountLayout.balances[msg.sender] -= amount;
    accountLayout.partyBAllocatedBalances[msg.sender][partyA] += amount;
}
```
The depositAndAllocateForPartyB function allows the users to deposit and allocate their accounts in a single transaction. Within the function, it calls the depositForPartyB function followed by the allocateForPartyB function. The function passes the same amount into both depositForPartyB and allocateForPartyB functions. However, the problem is that one accepts amount in native precision (e.g. 6 decimals) while the other accepts amount in scaled decimals (e.g. 18 decimals).
Assume that Alice calls the depositAndAllocateForPartyB function and intends to deposit and allocate 1000 USDC. Thus, she sets the amount of the depositAndAllocateForPartyB function to 1000e6 as the precision of USDC is 6.
The depositForPartyB function at Line 78 will work as intended because it will automatically be scaled up to internal accounting precision (18 decimals) within the function, and 1000 USDC will be deposited to her account.
The allocateForPartyB at Line 79 will not work as intended. The function expects the amount to be in internal accounting precision (18 decimals), but an amount in native precision (6 decimals for USDC) is passed in. As a result, only 0.000000001 USDC will be allocated to her account.
ontracts/facets/Account/AccountFacet.sol#L74
File: AccountFacet.sol
```solidity
function depositAndAllocateForPartyB(
    uint256 amount,
    address partyA
) external whenNotPartyBActionsPaused onlyPartyB {
    AccountFacetImpl.depositForPartyB(amount);
    AccountFacetImpl.allocateForPartyB(amount, partyA, true);
    emit DepositForPartyB(msg.sender, amount);
    emit AllocateForPartyB(msg.sender, partyA, amount);
}
```
Any users or external protocols utilizing the depositAndAllocateForPartyB to allocate 1000 USDC will end up only having 0.000000001 USDC allocated to their account, which might potentially lead to unexpected loss of funds due to the broken functionality if they rely on the accuracy of the outcome to perform certain actions dealing with funds/assets.
For instance, Bob's account is close to being liquidated. Thus, he might call the depositAndAllocateForPartyB function in an attempt to increase its allocated balance and improve its account health level to avoid being liquidated. However, the depositAndAllocateForPartyB is not working as expected, and its allocated balance only increased by a very small amount (e.g. 0.000000001 USDC in our example). Bob believed that his account was healthy, but in reality, his account was still in danger as it only increased by 0.000000001 USDC. In the next one or two blocks, the price swung, and Bob's account was liquidated.

## Recommendation
Scale the amount to internal accounting precision (18 decimals) before passing it to the allocateForPartyB function.
```solidity
function depositAndAllocateForPartyB(
    uint256 amount,
    address partyA
) external whenNotPartyBActionsPaused onlyPartyB {
    AccountFacetImpl.depositForPartyB(amount);
    uint256 amountWith18Decimals = (amount * 1e18) /
        (10 ** IERC20Metadata(GlobalAppStorage.layout().collateral).decimals());
    AccountFacetImpl.allocateForPartyB(amountWith18Decimals, partyA, true);
    emit DepositForPartyB(msg.sender, amount);
    emit AllocateForPartyB(msg.sender, partyA, amount);
}
```
