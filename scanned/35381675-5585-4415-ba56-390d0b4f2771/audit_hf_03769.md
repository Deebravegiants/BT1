# [M] token() function should return the address of

## Summary
Severity: Medium
Contest weight: 0.5950
Dataset id: 19942
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
In contract nwToken, function token() should return the address of the asset token
which, after migration, should be the nwToken address and not the cToken from
which the funds were migrated.
The functionalities Notional uses related to Compound V2 are located in contracts
CompoundHandler and cTokenAggregator, and in the scope of this contest, they are
merged into contract nwToken.
Function token() is a function of AssetRateAdapter contract, which is the base
contract of cTokenAggregator, and is supposed to return the address of the new
wrapper token after migration nwToken, but instead returns the address of the old
cToken. This fact makes not possible to use the nwToken as asset rate oracle when
enabling cash groups for a currency.
From contract GovernanceAction:
function enableCashGroup(
uint16 currencyId,
AssetRateAdapter assetRateOracle,
CashGroupSettings calldata cashGroup,
string calldata underlyingName,
string calldata underlyingSymbol
) external override onlyOwner {
_checkValidCurrency(currencyId);
{
// Cannot enable fCash trading on a token with a max collateral balance
Token memory assetToken = TokenHandler.getAssetToken(currencyId);
Token memory underlyingToken =
TokenHandler.getUnderlyingToken(currencyId);
require(
assetToken.maxCollateralBalance == 0 &&
underlyingToken.maxCollateralBalance == 0
); // dev: cannot enable trading, collateral cap
}
_updateCashGroup(currencyId, cashGroup);
_updateAssetRate(currencyId, assetRateOracle);
// Creates the nToken erc20 proxy that routes back to the main contract
nTokenERC20Proxy proxy = new nTokenERC20Proxy(
nTokenERC20(address(this)),
currencyId,
underlyingName,
underlyingSymbol
);
nTokenHandler.setNTokenAddress(currencyId, address(proxy));
emit DeployNToken(currencyId, address(proxy));
}
...
function _updateAssetRate(uint16 currencyId, AssetRateAdapter rateOracle)
internal {
// If rate oracle refers to address zero then do not apply any updates here,
this means
// that a token is non mintable.
Token memory assetToken = TokenHandler.getAssetToken(currencyId);
if (address(rateOracle) == address(0)) {
// Sanity check that unset rate oracles are only for non mintable tokens
require(assetToken.tokenType == TokenType.NonMintable, "G: invalid asset
rate");
} else {
// Sanity check that the rate oracle refers to the proper asset token
address token = AssetRateAdapter(rateOracle).token();
require(assetToken.tokenAddress == token, "G: invalid rate oracle");
uint8 underlyingDecimals;
if (currencyId == Constants.ETH_CURRENCY_ID) {
// If currencyId is one then this is referring to cETH and there is
no underlying() to call
underlyingDecimals = Constants.ETH_DECIMAL_PLACES;
} else {
address underlyingTokenAddress =
AssetRateAdapter(rateOracle).underlying();
Token memory underlyingToken =
TokenHandler.getUnderlyingToken(currencyId);
// Sanity check to ensure that the asset rate adapter refers to the
correct underlying
require(underlyingTokenAddress == underlyingToken.tokenAddress, "G:
invalid adapter");
underlyingDecimals = ERC20(underlyingTokenAddress).decimals();
}
// Perform this check to ensure that decimal calculations don't overflow
require(underlyingDecimals <= Constants.MAX_DECIMAL_PLACES);
mapping(uint256 => AssetRateStorage) storage store =
LibStorage.getAssetRateStorage();
store[currencyId] = AssetRateStorage({
rateOracle: rateOracle,
underlyingDecimalPlaces: underlyingDecimals
});
emit UpdateAssetRate(currencyId);
}
}
We see that when Governance tries to enable a cash group, the user passes to the
enableCashGroup an asset rate oracle that is used in the internal call to
_updateAssetRate. The following lines would make the call revert if trying to pass
the nwToken address as rate oracle:
...
address token = AssetRateAdapter(rateOracle).token();
require(assetToken.tokenAddress == token, "G: invalid rate oracle");
...
because token would be old cToken but assetToken.tokenAddress would be the
address of nwToken.
After migration, the rate adapter for each of the four currencies migrated is set to
cts-v2-private/contracts/external/patchfix/MigrateCTokens.sol#L107-L109
As we can see in the tests, all four nwTokens are created passing the address of
the old cToken as COMPOUND_TOKEN in the constructor.
```

## Recommendation
```solidity
Change the following function in contract nwToken:
function token() external view returns (address) {
return COMPOUND_TOKEN;
}
With this:
function token() external view returns (address) {
return address(this);
}
```
