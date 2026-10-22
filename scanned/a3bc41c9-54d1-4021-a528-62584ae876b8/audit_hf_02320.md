# [M] Insufficient Collateral in Controller::_settleVault()

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 12632
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Controller contract is the entry point for all users, it manages all the opened vaults for all sellers, and also takes care of the redeem operation for buyers.
The _settleVault() function settles a vault after expiry and removes the net collateral after both long and short oToken payouts have been settled. It calls getExcessCollateral() to calculate the exact amount of collateral returned to users. This function also returns a flag indicating whether there is excess margin in the vault.
```solidity
function _settleVault(Actions.SettleVaultArgs memory _args)
    internal
    onlyAuthorized(msg.sender, _args.owner)
{
    require(_checkVaultId(_args.owner, _args.vaultId), "Controller: invalid vault id");
    MarginVault.Vault memory vault = getVault(_args.owner, _args.vaultId);
    bool hasShort = _isNotEmpty(vault.shortOtokens);
    bool hasLong = _isNotEmpty(vault.longOtokens);
    require(hasShort && hasLong, "Controller: Can't settle vault with no otoken");
    OtokenInterface otoken = hasShort ? OtokenInterface(vault.shortOtokens[0]) : OtokenInterface(vault.longOtokens[0]);
    address underlying = otoken.underlyingAsset();
    address strike = otoken.strikeAsset();
    address collateral = otoken.collateralAsset();
    uint256 expiry = otoken.expiryTimestamp();
    require(now >= expiry, "Controller: can not settle vault with un-expired otoken");
    require(
        isSettlementAllowed(underlying, strike, collateral, expiry),
        "Controller: asset prices not finalized yet"
    );
    (uint256 payout, ) = calculator.getExcessCollateral(vault);
    if (hasLong) {
        OtokenInterface longOtoken = OtokenInterface(vault.longOtokens[0]);
        longOtoken.burnOtoken(address(pool), vault.longAmounts[0]);
    }
    delete vaults[_args.owner][_args.vaultId];
    pool.transferToUser(collateral, _args.to, payout);
    emit VaultSettled(_args.owner, _args.to, address(otoken), _args.vaultId, payout);
}
```
However, if the price of collateral drops a lot, it may not be able to pay for the option. Fortunately, only whitelisted oTokens can be deposited as collateral. The dev team will make sure the otokenCollateralAsset is the same with otokenStrikeAsset.

## Recommendation
Make sure the otokenCollateralAsset is the same with otokenStrikeAsset in Controller::_depositCollateral().
