# [H] Adversary can steal approved tOLPs to Magnetar via `_paricipateOnTOLP`

## Summary
Severity: High
Chain: Smart contract
Component: 2024-02-tapioca
Published: 2024-03-12
Source: https://github.com/code-423n4/2024-02-tapioca-findings/issues/54
Type: code-finding

## Details
# Lines of code

https://github.com/Tapioca-DAO/tapioca-periph/blob/032396f701be935b04a7e5cf3cb40a0136259dbc/contracts/Magnetar/modules/MagnetarMintCommonModule.sol#L89


# Vulnerability details

## Impact
User can steal pre-approved tOLPs to Magnetar 

## Proof of Concept
Any user could steal any approved tOLP to Magnetar.
This is because within the Magnetar call, if the user has not minted a tOLP NFT, they can participate with any id they wish, by inputting it in `participateData`.

```solidity
    function _participateOnTOLP(
        IOptionsParticipateData memory participateData,
        address user,
        address lockDataTarget,
        uint256 tOLPTokenId
    ) internal {
        if (!cluster.isWhitelisted(0, participateData.target)) {
            revert Magnetar_TargetNotWhitelisted(participateData.target);
        }

        // Check tOLPTokenId
        if (participateData.tOLPTokenId != 0) {
            if (participateData.tOLPTokenId != tOLPTokenId && tOLPTokenId != 0) {
                revert Magnetar_tOLPTokenMismatch();
            }

            tOLPTokenId = participateData.tOLPTokenId;  // @audit - does not verify sender owns that token
        }
        if (tOLPTokenId == 0) revert Magnetar_ActionParamsMismatch();

        IERC721(lockDataTarget).approve(participateData.target, tOLPTokenId);
        uint256 oTAPTokenId = ITapiocaOptionBroker(participateData.target).participate(tOLPTokenId);

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-02-tapioca-findings/issues/54_
