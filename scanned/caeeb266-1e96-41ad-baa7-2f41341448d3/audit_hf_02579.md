# [M] RedemptionVaultWIthBUIDL.sol#redeemInstantwill

## Summary
Severity: Medium
Contest weight: 0.4603
Dataset id: 13944
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RedemptionVaultWIthBUIDL.sol#redeemInstant will always DoS due to incorrect contract call.
In RedemptionVaultWIthBUIDL contract, it uses the BUIDL contracts to redeem BUIDL tokens to USDC tokens, and users are expected to always receive USDC tokens.
On Ethereum, the buidlRedemption is this contract https://etherscan.io/address/0x31D3F59Ad4aAC0eeE2247c65EBE8Bf6E9E470a53#readContract. The buidlRedemption.liquidity() is this contract https://etherscan.io/address/0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48, which is USDC.
The issue here is, the code wrongly assumes buidlRedemption.liquidity() is the liquiditySource, when it should be the USDC token. This will always lead to DoS for the buidlLiquiditySource.token() call in redeemInstant since USDC does not support .token() call.
```solidity
function initialize(
    address _ac,
    MTokenInitParams calldata _mTokenInitParams,
    ReceiversInitParams calldata _receiversInitParams,
    InstantInitParams calldata _instantInitParams,
    address _sanctionsList,
    uint256 _variationTolerance,
    uint256 _minAmount,
    FiatRedeptionInitParams calldata _fiatRedemptionInitParams,
    address _requestRedeemer,
    address _buidlRedemption
) external initializer {
    __RedemptionVault_init(
        _ac,
        _mTokenInitParams,
        _receiversInitParams,
        _instantInitParams,
        _sanctionsList,
        _variationTolerance,
        _minAmount,
        _fiatRedemptionInitParams,
        _requestRedeemer
    );
    _validateAddress(_buidlRedemption, false);
    buidlRedemption = IRedemption(_buidlRedemption);
    buidlSettlement = ISettlement(buidlRedemption.settlement());
    buidlLiquiditySource = ILiquiditySource(buidlRedemption.liquidity());
    buidl = IERC20(buidlRedemption.asset());
}
function redeemInstant(
    address tokenOut,
    uint256 amountMTokenIn,
    uint256 minReceiveAmount
)
external
override
whenFnNotPaused(this.redeemInstant.selector)
onlyGreenlisted(msg.sender)
onlyNotBlacklisted(msg.sender)
onlyNotSanctioned(msg.sender)
{
    // BUG: This will always fail.
    tokenOut = buidlLiquiditySource.token();
    ...
}
```
The correct implementation would be to use buidlSettlement.liquiditySource() to get the liquidity source, since there is an API for that in the buidlSettlement contract https://etherscan.io/address/0x57Dd4E92712b0fBC8d3f3e3645EebCf2600aCef0#readContract.
RedemptionVaultWIthBUIDL.sol#redeemInstant will always DoS.

## Recommendation
Use buidlSettlement.liquiditySource() to get the liquidity source. Also add the liquiditySource API to ISettlement.
