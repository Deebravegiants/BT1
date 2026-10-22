# [H] MJR-3 Approve / TransferFrom multiple withdrawal attack

## Summary
Severity: High
Contest weight: 0.2680
Dataset id: 13575
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
This known issue is documented here: https://github.com/ethereum/EIPs/issues/738.
Summary / example of the attack:
1. Alice allows Bob to transfer N of Alice's tokens (N>0) by calling approve method on Token smart contract passing Bob's address and N as method arguments
2. After some time, Alice decides to change from N to M (M>0) the number of Alice's tokens Bob is allowed to transfer, so she calls approve method again, this time passing Bob's address and M as method arguments
3. Bob notices Alice's second transaction before it was mined and quickly sends another transaction that calls transferFrom method to transfer N Alice's tokens somewhere
4. If Bob's transaction is executed before Alice's transaction, then Bob will successfully transfer N Alice's tokens and will gain an ability to transfer another M tokens
5. Before Alice noticed that something went wrong, Bob calls transferFrom method again, this time to transfer M Alice's tokens.
So, Alice's attempt to change Bob's allowance from N to M (N>0 and M>0) made it possible for Bob to transfer N+M of Alice's tokens, while Alice never wanted to allow so many of her tokens to be transferred by Bob.

## Recommendation
We recommend adding additional sanity checks to the approve() function and using the increaseAllowance() / decreaseAllowance() workaround functions:
```solidity
require((amount == 0) || (allowed[msg.sender][spender] == 0));
```
