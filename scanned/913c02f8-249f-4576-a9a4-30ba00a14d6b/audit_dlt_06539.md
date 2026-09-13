# [M] `_createTriple()` logic do not follow the intended design mentioned in documentation

## Summary
Severity: Medium
Chain: Smart contract
Component: Intuition
Published: 2024-06-27
Source: https://github.com/hats-finance/Intuition-0x538dbadc50cc87b281cd655f1edbc6ebda02a66a/issues/55
Type: hats-finding

## Details
**Github username:** @itsabinashb
**Twitter username:** akatabletos
**Submission hash (on-chain):** 0x3219a50d45531bb4608fd533f3fb64d9b794f62810d962c576e72e28c7afd21a
**Severity:** medium

**Description:**
**Description**\
The current logic of `_createTriple()` does not match with intended design mentioned in documentation, in case of adding `Triples` as `Atom` in `Tripple`.

**Attack Scenario**\

See the PoC section.
**Attachments**

1. **Proof of Concept (PoC) File**\
In [documention](https://intuition.gitbook.io/intuition-contracts/introduction/definition-and-glossary) it was mentioned how a `Triple` should be treated:

>Intuition’s atomic unit of knowledge. [Atoms] can be used to represent [Subjects], [Predicates], [Objects], and [Triples]. All [Triples] are a composition of [Atoms], and [Triples] can be used as [Atoms] in other [Triples].

See the last sentense: *[Triples] can be used as [Atoms] in other [Triples]*,
but if you see the code in [`_createTriple()`](https://github.com/0xIntuition/intuition-contracts/blob/b88caf1106e713f1da9e114f249ea056f5e555a0/src/EthMultiVault.sol#L594-L597) :

```solidity
            // make sure that each id is not a triple vault id
            if (isTripleId(tripleAtomIds[i])) {
                revert Errors.MultiVault_VaultIsTriple(tripleAtomIds[i]);
            }
```
it is reverting when the one of 3 ids are of `Triple`. So, as result the `Triple` cannot be used as `Atom` while it should be.\
2. **Revised Code File (Optional)**

<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->
