# [C] C-2 getvirtualprice() can be manipulated

## Summary
Severity: Critical
Contest weight: 0.2409
Dataset id: 7064
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
getvirtualprice() can be manipulated by directly transferring tokens to the pools. The thing is that directly transferred tokens can be skimmed via the exchange_received() function:
CurveStableSwapNG.vy#L1629
CurveStableSwapMetaNG.vy#L1610
One example of an attack that can make a profit for a hacker is:
1. Directly transfer one of the tokens to a basepool that was added to a metapool.
2. getvirtualprice() increases, because D increases and total_supply remains the same.
3. The hacker can call removeliquidityonecoin() in metapool. Due to the increased virtualprice of the basepool LP token, it will cost a lot less to remove coin[0] from meta_pool.
4. After this, the hacker can call exchangereceived in the basepool and return the deposited in (1) funds.
The test scenario was sent to the client during the audit.
This finding is classified as critical because many protocols rely on the virtual_price of the pool (even Curve relies on it), and manipulation of the virtual_price is very dangerous.

## Recommendation
We recommend updating the design of the exchangereceived() and balances() functions so that they work with donations correctly.
