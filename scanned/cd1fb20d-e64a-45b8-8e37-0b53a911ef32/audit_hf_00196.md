# [M] createBasket re-entrancy

## Summary
Severity: Medium
Contest weight: 0.0450
Dataset id: 1031
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a potential re‑entrancy flaw in the Factory contract’s createBasket function. The function iterates over a list of token addresses and performs operations that may call external ERC‑20‑like contracts, such as transferring or approving tokens. Because the contract does not use a nonReentrant guard, a malicious token contract could execute a callback during one of those external calls and re‑enter createBasket before the original execution finishes. The root cause is the absence of a re‑entrancy protection mechanism while the function performs untrusted external calls inside a loop. An attacker could craft a token that, when its transfer/approve hook is invoked, calls back into createBasket with specially crafted parameters, causing the loop to be executed a second time or altering internal state such as basket identifiers or accounting mappings. This could lead to duplicated basket creation, mismatched accounting, or the unintended allocation of tokens to the attacker, effectively allowing funds to be siphoned or the protocol’s state to become inconsistent. The issue surfaces whenever createBasket is called with at least one token that implements a callback hook (e.g., ERC777’s tokensReceived or a malicious ERC20 whose transfer function calls back into the Factory). All users who rely on the basket creation mechanism, as well as the protocol’s overall accounting, are affected because the protocol may record incorrect balances or allow an attacker to create baskets that appear funded but are not. The flaw was identified during a manual audit that flagged the missing nonReentrant modifier on a function that interacts with external contracts. It may be hard to notice in testing because typical ERC20 tokens do not trigger callbacks, so the re‑entrancy path only manifests with specially crafted tokens. Conceptually, the fix is to apply a re‑entrancy guard (e.g., OpenZeppelin’s nonReentrant modifier) to the createBasket function, ensuring that any re‑entrant call will be rejected while the first execution is still in progress. This aligns the function with the generic class of re‑entrancy bugs where untrusted external calls are made without a protection pattern. From a user’s perspective, a basket may appear to be created successfully but later show missing or altered token balances, leading to confusion such as "my basket shows zero tokens after creation" or "the protocol reports my funds have disappeared". The expectation that creating a basket will securely lock the specified tokens is violated, and the actual outcome can be a silent loss of assets or corrupted accounting records.

## Recommendation
Add `nonReentrant` modifier to the declaration of createBasket.

I agree that since the function can potentially interact with any ERC20like token, the function is vulnerable to re-entrancy, because we don't have any specific POC for an attack, this is a medium severity finding
