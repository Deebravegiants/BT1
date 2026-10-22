# [H] 5.1 Heap Data Structure Can Be Spammed

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness High Version 1 Risk Accepted

The users' supply and borrow information is stored in Heap data structures. The parameter
_maxSortedUsers sets the maximum sorted user amount in order to limit the gas spent on updating the
Heap. The data structure would halve the length of the Heap when maxSortedUsers is exceeded.
However, this behavior would potentially put an incoming user to a higher priority than an existing one.
This behavior can be abused by bad actors to fill the ordered portion of the Heap with dust:

Consider the following example:

- maxSortedUsers is set to 4.
- Step 1: User 1 and user 2 are legitimate users that supplied 400 and 300 tokens respectively.
- Step 2: An attacker now supplies 600, 500 and 1 token with three different addresses.
- Step 3: The attacker withdraws 599 and 499 tokens from accounts 3 and 4.

The described behavior is detailed in Figure 1. Blue boxes show accounts in the ordered portion of the
Heap, green boxes show accounts in the non-ordered portion.


```
Figure 1: Spam attack on the Heap
```
As a result, the supplied liquidity of users 1 and 2 is now only reachable after the dust of the attacker's
accounts has been matched.

Risk accepted:

Morpho Labs accepts the risk with the following statement:

```
We know that the heap structure has still some drawbacks (even if it’s better than the double linked
list implemented on the compound contracts) and we acknowledge the manipulation of the heap. The
spam attack is likely to be costly to conduct, moreover, if users come after with greater amounts the
dust accounts will be pushed outside the heap.
```
