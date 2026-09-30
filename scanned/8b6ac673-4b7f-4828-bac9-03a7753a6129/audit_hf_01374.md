# [C] C-3 Read-only reentrancy in metapool with an old basepool

## Summary
Severity: Critical
Contest weight: 0.2082
Dataset id: 7065
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Old base pools cannot be added to CurveStableSwapFactory. Using an old base pool in meta_pool can lead to read-only reentrancy attacks because of the possible manipulation of the virtual price of a base pool LP token. There is a possible read-only reentrancy attack with a call to getvirtualprice in a metapool (At the line CurveStableSwapMetaNG.vy#L457). Virtual price can be incorrectly increased, and that rate can be used during a swap from base pool LP to the second coin in metapool. It will work with old base pools that use ETH (new ones have a reentrancy lock on the getvirtualprice function).
This issue has been assigned a CRITICAL severity level because working with old base pools that contain ETH will lead to rate manipulation and funds loss (exchanging tokens using manipulated prices).

## Recommendation
We recommend adding checks to the CurveStableSwapFactoryNG contract when base pools are added. It shouldn't be possible to add pools paired with ETH.
2.2 High
