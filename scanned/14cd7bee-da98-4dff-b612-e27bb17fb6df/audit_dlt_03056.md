# [M] User could be forced to withdraw more amount than desired when calling `retrieveFromStrategy`

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-tapioca
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-tapioca-findings/issues/1346
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTStrategyModule.sol#L89-L120


# Vulnerability details

## Impact
User could be forced to withdraw more amount than desired when calling `retrieveFromStrategy`, because they can not specify the amount of yieldbox balance to permit.

## Proof of Concept
    function retrieveFromStrategy(
        address _from,
        uint256 amount,
        uint256 share,
        uint256 assetId,
        uint16 lzDstChainId,
        address zroPaymentAddress,
        bytes memory airdropAdapterParam
    ) external payable {
        require(amount > 0, "TOFT_0");

        bytes32 toAddress = LzLib.addressToBytes32(msg.sender);

        bytes memory lzPayload = abi.encode(
            PT_YB_RETRIEVE_STRAT,
            LzLib.addressToBytes32(_from),
            toAddress,
            amount,
            share,
            assetId,
            zroPaymentAddress
        );
        _lzSend(
            lzDstChainId,
            lzPayload,
            payable(msg.sender),
            zroPaymentAddress,
            airdropAdapterParam,
            msg.value
        );
        emit SendToChain(lzDstChainId, msg.sender, toAddress, amount);
    }

When a user initiates a cross chain request to `retrieveFromStrategy`, they need to sign a EIP712 permit to approve YieldBox for TOFT contract. Attacker can take the signature and frontrun the tx with `{from: user, amount: larger than user wishes, approvals:user's signature}` to force the user to withdraw more amount than desired.
If user forgets to revoke their approvals, the attack could also happen. Attacker can withdraw the user's yieldbox balance without being noticed.

Note: I believe it is a mistake that `ICommonData.IApproval[] calldata approvals` is missing at `retrieveFromStrategy` input param. Even though this is intended, the issue still exists as user still needs to approve YieldBox for TOFT contract in other way.

## Tools Used
Manual

## Recommended Mitigation Steps
Add more refined allowance control for YieldBox. (just like erc20)





## Assessed type

Context
