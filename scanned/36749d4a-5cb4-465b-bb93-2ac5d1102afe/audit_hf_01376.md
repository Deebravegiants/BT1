# [H] H-2 Incorrect storage update

## Summary
Severity: High
Contest weight: 0.1470
Dataset id: 7067
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
stored_balances is increased by dx_w_fee for metacoin in meta_pool here CurveStableSwapMetaNG.vy#L1065 but actually it should be increased by dx_w_fee that returned from the meta_add_liquidity because the actual increase in metacoin balance will be less than dx_w_fee from transfer_in due to possible fees on liquidity addition. This finding is classified as HIGH because the current implementation of the meta_pool will become broken after one call of the exchange_underlying() function (exchange_received will not work after this).

## Recommendation
We recommend updating the storage value with the correct value.
