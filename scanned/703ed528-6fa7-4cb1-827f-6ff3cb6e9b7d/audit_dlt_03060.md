# [M] Airdropped tokens can be stolen by a bot

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1300
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L227


# Vulnerability details

## Impact

Most of the packetTypes, when received on the remote chain, are supposed to send a message to another chain.
To send that callback message usually a certain amount of gas is airdropped to a remote chain to execute that message.
If we look at the reception logic for [`leverageUp`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L227) the airdropped amount is supposed to be transferred to the address of the `TapiocaOFT` contract.
This is an issue because if anything reverts here the airdropped amount is left sitting in the `USDO` contract and can be stolen by a bot.
This is rather a common occurrence through the codebase and usually, in case of a revert the airdropped amount will be left in the `USDO`, `TapOFT`, or `MagnetarV2` contracts, and in all these places it can be stolen by a bot.
There is a high likelihood of this occurring quite often because it takes (1-5 min. or more) for a Relayer to deliver a message to the remote chain during which the airdropped amount might not be sufficient to execute the callback message, or something else can revert.

## Proof of Concept

I have already described the issue in the impact section and here I will describe how a bot can steal the airdropped amount.
The bot can use the same message pathway, e.g. [`sendForLeverage`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/BaseUSDO.sol#L284) -> [`leverageUp`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/BaseUSDO.sol#L423) to steal all the balance of the `USDO` contract.

1. The bot calls [`sendForLeverage`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/BaseUSDO.sol#L284) function with a very small amount of [`USDO`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L70), e.g. that is his cost of attack.
2. When it is received on the remote chain out of [all the parameters to the function](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L198-L252) he would need to deploy fake contracts which do nothing for 
[`ISwapper(externalData.swapper).buildSwapData(..)`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L199), [`ISwapper(externalData.swapper).swap(...)`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L209), [`ITapiocaOFTBase(externalData.tOft).wrap(...)`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L218).
3. However, for the [`ITapiocaOFT(externalData.tOft).sendToYBAndBorrow{value: address(this).balance}`](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOLeverageModule.sol#L226C20-L226C20) this would need to be the address of his malicious contract which implements the `sendToYBAndBorrow` and would just receive the `address(this).balance`.

```solidity
contract MaliciousReceiver {

    function sendToYBAndBorrow(
        address _from,
        address _to,
        uint16 lzDstChainId,
        bytes calldata airdropAdapterParams,
        IBorrowParams calldata borrowParams,
        ICommonData.IWithdrawParams calldata withdrawParams,
        ICommonData.ISendOptions calldata options,
        ICommonData.IApproval[] calldata approvals
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1300_
