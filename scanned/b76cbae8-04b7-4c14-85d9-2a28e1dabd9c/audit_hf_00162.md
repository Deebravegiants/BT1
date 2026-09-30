# [H] Reentrancy in settleAuction

## Summary
Severity: High
Contest weight: 0.4935
Dataset id: 892
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a classic re‑entrancy flaw located in the `settleAuction` function of the DeFi protocol’s basket contract. The function calls an external `withdrawBounty` routine, which in turn triggers a transfer of a bounty token using the ERC‑20 `transfer` method, before it updates the internal `auctionOngoing` flag to false. Because the state change (setting `auctionOngoing = false`) occurs after the external call, a malicious bounty token can re‑enter `settleAuction` during the transfer callback. The root cause is a violation of the Checks‑Effects‑Interactions pattern: the contract makes an external call prior to completing its own internal state updates. An attacker who controls the bounty token can craft a `transfer` implementation that invokes `settleAuction` again with crafted parameters. Since the first call has already satisfied all the prerequisite checks, the re‑entered call passes, invokes `setNewWeights`, and overwrites the pending weight structure with attacker‑chosen values. When the original `settleAuction` resumes, it again calls `setNewWeights`, now applying the malicious weights. The attacker then proceeds to burn all of his basket shares in the same transaction, causing the basket’s assets to be transferred to the attacker’s address. This sequence results in the complete draining of funds that were meant to be locked in the basket, effectively disappearing from the protocol’s balance. The issue surfaces only when a publisher—who is allowed to call the `onlyPublisher` functions such as `publishNewIndex`—submits a malicious bounty token alongside a legitimate auction settlement. Consequently, any user who holds basket shares or relies on the auction’s outcome can lose their value. The flaw was discovered during a Code4rena audit; the warden produced a proof‑of‑concept that demonstrated the re‑entrancy by deploying a malicious ERC‑20 token and invoking the vulnerable flow within a single transaction. The problem is subtle because the external token transfer appears innocuous and the state flag is updated later, making manual code reviews prone to overlooking the re‑entrancy window. To remediate the issue, the contract should adopt the Checks‑Effects‑Interactions pattern: move all external calls—including the bounty token transfer and `withdrawBounty`—to the end of `settleAuction`, and set `auctionOngoing = false` immediately after the initial checks. This ensures that any re‑entrant call finds the auction already marked as finished, blocking the secondary execution path. The fix also aligns with best practices for handling external token interactions, eliminating the state‑corruption window that allowed the attacker to manipulate pending weights and ultimately seize the basket’s assets.

## Proof of Concept
1. The publisher (a contract) will propose new valid index and bond the auction.

To settle the auction, the publisher will execute the following steps in the same transaction:

  2. Add a bounty of an ERC20 contract with a malicious `transfer()` function.
  3. Settle the valid new weights correctly (using `settleAuction()` with the correct parameters, and passing the malicious bounty id).
  4. `settleAuction()` will call `withdrawBounty()` which upon transfer will call the publisher’s malicious ERC20 contract.
  5. The contract will call `settleAuction()` again, with empty parameters. Since the previous call’s effects have already set all the requirements to be met, `settleAuction()` will finish correctly and call `setNewWeights()` which will set the new valid weights and set `pendingWeights.pending = false`.
  6. Still inside the malicious ERC20 contract transfer function, the attacker will now call the basket’s `publishNewIndex()`, with weights that will transfer all the funds to him upon his burning of shares. This call will succeed to set new pending weights as the previous step set `pendingWeights.pending = false`.
  7. Now the malicious `withdrawBounty()` has ended, and the original `settleAuction()` is resuming, but now with malicious weights in `pendingWeights` (set in step 6). `settleAuction()` will now call `setNewWeights()` which will set the basket’s weights to be the malicious pending weights.
  8. Now `settleAuction` has finished, and the publisher (within the same transaction) will `burn()` all his shares of the basket, thereby transferring all the tokens to himself.

POC exploit: Password to both files: “exploit”. AttackPublisher.sol , to be put under contracts/contracts/Exploit: <https://pastebin.com/efHZjstS> ExploitPublisher.test.js , to be put under contracts/test: <https://pastebin.com/knBtcWkk>

## Recommendation
In `settleAuction()`, move `basketAsERC20.transfer()` and `withdrawBounty()` to the end of the function, conforming with Checks Effects Interactions pattern.

This is a re-entrancy finding.

There is no denying that the code is vulnerable to re-entrancy

The warden identified the way to exploit re-entrancy by using a malicious bounty token.

I think the finding is valid and the warden has shown how to run re-entrnacy.

That said the POC the warden shows requires calling `publishNewIndex` which is a `onlyPublisher` function. This exploit would be contingent on the publisher rugging the basket.

The code is:

  * Vulnerable to re-entancy
  * The warden showed how to trigger it


Despite the fact that the POC is flawed, I believe this finding highlights a different vector for re-entrancy (bounty token transfers) as such I agree with a high severity
