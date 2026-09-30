# [H] pUSDeVault::startYieldPhase should not remove supported vaults from being supported or should prevent new supported vaults once in the yield phase

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23528
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The intention of pUSDeVault::startYieldPhase is to convert assets from existing supported vaults into USDe in order to then stake the vault's total USDe into the sUSDe vault. However because this ends up calling MetaVault::removeVaultAndRedeemInner, all the supported vaults are also removed after their assets are converted.  
But new vaults can continue to be added during the yield phase, so it makes no sense to remove all supported vaults at this time.  
Impact: The contract owner will need to re-add all the previously enabled supported vaults causing all user deposits to revert until this is done.

## Proof of Concept
```solidity
function test_supportedVaultsRemovedWhenYieldPhaseEnabled() external {
    // supported vault prior to yield phase
    assertTrue(pUSDe.isAssetSupported(address(eUSDe)));
    // user1 deposits $1000 USDe into the main vault
    uint256 user1AmountInMainVault = 1000e18;
    USDe.mint(user1, user1AmountInMainVault);
    vm.startPrank(user1);
    USDe.approve(address(pUSDe), user1AmountInMainVault);
    uint256 user1MainVaultShares = pUSDe.deposit(user1AmountInMainVault, user1);
    vm.stopPrank();
    // admin triggers yield phase on main vault
    pUSDe.startYieldPhase();
    // supported vault was removed when initiating yield phase
    assertFalse(pUSDe.isAssetSupported(address(eUSDe)));
    // but can be added back in?
    pUSDe.addVault(address(eUSDe));
    assertTrue(pUSDe.isAssetSupported(address(eUSDe)));
    // what was the point of removing it if it can be re-added
    // and used again during the yield phase?
}
```

## Recommendation
Recommended Mitigation: Don't remove all supported vaults when calling pUSDeVault::startYieldPhase; just convert their assets to USDe but continue to allow the vaults themselves to be supported and accept future deposits.  
Alternatively don't allow supported vaults to be added during the yield phase (apart from sUSDe which is added when the yield phase is enabled). In this case removing them when enabled the yield phase is fine, but add code to disallow adding them once the yield phase is enabled.
