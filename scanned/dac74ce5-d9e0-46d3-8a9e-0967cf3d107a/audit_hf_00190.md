# [H] `FeePoolV0.sol#distributeMochi

## Summary
Severity: High
Contest weight: 0.2482
Dataset id: 1020
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`distributeMochi()` will call `_buyMochi()` to convert `mochiShare` to Mochi token and call `_shareMochi()` to send Mochi to vMochi Vault and veCRV Holders. It wont touch the `treasuryShare`.

However, in the current implementation, `treasuryShare` will be reset to `0`. This is unexpected and will cause the protocol fee can not be properly accounted for and collected.

[`FeePoolV0.sol#L79` L95](https://github.com/code-423n4/2021-10-mochi/blob/8458209a52565875d8b2cefcb611c477cefb9253/projects/mochi-core/contracts/feePool/FeePoolV0.sol#L79-L95)
    
    function _shareMochi() internal {
        IMochi mochi = engine.mochi();
        uint256 mochiBalance = mochi.balanceOf(address(this));
        // send Mochi to vMochi Vault
        mochi.transfer(
            address(engine.vMochi()),
            (mochiBalance * vMochiRatio) / 1e18
        );
        // send Mochi to veCRV Holders
        mochi.transfer(
            crvVoterRewardPool,
            (mochiBalance * (1e18 - vMochiRatio)) / 1e18
        );
        // flush mochiShare
        mochiShare = 0;
        treasuryShare = 0;
    }

## Recommendation
No recommendation
