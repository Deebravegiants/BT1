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
    ) external payable {
        // do nothing
    }
}
```

If speed is of importance here the attacker can even pull off a more sophisticated attack which would do the following:

1. First he intentionally sends a transaction that fails in the `leverageUp` function, and it would fail due to the following mechanism:

```solidity
contract MaliciousReceiver {

    bool drainGas = false;

    function sendToYBAndBorrow(
        address _from,
        address _to,
        uint16 lzDstChainId,
        bytes calldata airdropAdapterParams,
        IBorrowParams calldata borrowParams,
        ICommonData.IWithdrawParams calldata withdrawParams,
        ICommonData.ISendOptions calldata options,
        ICommonData.IApproval[] calldata approvals
    ) external payable {
            if (!drainGas) revert();
    }

    function setDrainGas(bool _drainGas) external {
        drainGas = _drainGas;
    }

    receive() external payable {}
}
```
2. Then he goes ahead and calls `setDrainGas(true)` on the malicious contract. And monitors if any of the user's transactions are failing, and then he can instantly on the same chain just retry his message through [retryMessage](https://github.com/Tapioca-DAO/tapioca-sdk-audit/blob/90d1e8a16ebe278e86720bc9b69596f74320e749/src/contracts/lzApp/NonblockingLzApp.sol#L46) and steal all the balance.


## Tools Used
- Manual review
- Foundry

## Recommended Mitigation Steps

This is a more broad architectural issue of the codebase which I discussed in my analysis review, and it goes back to the fact that airdropped gas tokens do not belong to the user.
An immediate fix would be to in the case of function revert to send the airdropped amount back to the user. This can be inserted in the following [place]:(https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/BaseUSDO.sol#L375-L397)

```solidity
    function _executeOnDestination(
        Module _module,
        bytes memory _data,
        uint16 _srcChainId,
        bytes memory _srcAddress,
        uint64 _nonce,
        bytes memory _payload
    ) private {
        (bool success, bytes memory returnData) = _executeModule(
            _module,
            _data,
            true
        );
        if (!success) {
            if (address(this).balance != 0) {
                (bool sent, ) = msg.sender.call{value: address(this).balance}("");
                if (!sent) {
                    // emit an event
                }
            }
            _storeFailedMessage(
                _srcChainId,
                _srcAddress,
                _nonce,
                _payload,
                returnData
            );
        }
    }
```

## Other occurrences

Anywhere in the code where `address{this}.balance` or `msg.value` is passed to the `_lzSend` if it fails it will remain in that contract and can be stolen. I haven't set up a case for stealing airdropped balances of TOFT contracts, since there is a more serious attack there which I described in my other issues.

- https://github.com/Tapioca-DAO/tapiocaz-audit/blob/master/contracts/tOFT/modules/BaseTOFTMarketModule.sol#L192-L193 - if execution fails in the `MagnetarMarketModule` contract it will be left sitting in the TOFT or in the MagnetarV2 contract depending on where it was airdropped.

- https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOMarketModule.sol#L205 - This assumes that the airdropped value is inside the MagnetarV2 contract since there is a [withdrawal](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/modules/MagnetarMarketModule.sol#L276) to other chain option, and if everything fails the airdropped token is left in the `MagnetarV2` contract.
- https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/master/contracts/usd0/modules/USDOOptionsModule.sol#L127

- https://github.com/Tapioca-DAO/tap-token-audit/blob/main/contracts/tokens/BaseTapOFT.sol#L229 - This same message pathway can be used to steal any balance of BaseTapOFT contract since `try twTap.claimAndSendRewards(tokenID, rewardTokens)`doesn't revert if rewardTokens are not valid tokens, e.g. are just some malicious contract.
- https://github.com/Tapioca-DAO/tap-token-audit/blob/main/contracts/tokens/BaseTapOFT.sol#L312

If the gas tokens remain as the balance of the MagnetarV2 contract the easiest way to steal them is to call [`withdrawToChain`](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/MagnetarV2.sol#L732) since it can be set up so [asset](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/main/contracts/Magnetar/modules/MagnetarMarketModule.sol#L725) is a malicious contract which just receives value.






## Assessed type

Other
