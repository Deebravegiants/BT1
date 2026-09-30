# [M] M-06 | Lacking LP Validations Allows For Malicious Intent

## Summary
Severity: Medium
Contest weight: 0.1373
Dataset id: 20866
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone can create a pool with the same base/quote tokens as well as the same params (i, k) as an 'oﬃcial' MIMSwap pool. An attacker could create such pools to steal liquidity away, or even worse implement such pools with rug pull functions. Since the Router does not validate the lp address, router functions can be used to interact with these malicious LPs. Attackers may interact with router functions intentionally to populate etherscan with transactions to their malicious pool. Users who see this may check the pool and see that the base/quote token and other params are correct, and end up interacting with that LP instead of the oﬃcial one. In fact, there may not even be an oﬃcial lp yet, i.e. attackers frontrun the creation of the LP once they know the address of the base/quote tokens. This often happens when a memecoin is launched with no frontend or oﬃcial site stating the correct lp address.

## Recommendation
In the Router contract, validate the lp address against the pools mapping in the Factory before allowing the function to continue executing.
