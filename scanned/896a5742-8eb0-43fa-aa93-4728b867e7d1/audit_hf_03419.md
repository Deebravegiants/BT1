# [M] `addCredit` DOS Attack

## Summary
Severity: Medium
Contest weight: 0.1537
Dataset id: 18663
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a denial‑of‑service condition caused by the addCredit function being callable by any address with no minimum ether requirement. Because addCredit updates the stored hash of a lien (liens[lienId] = keccak256(abi.encode(lien))) without restricting the caller, an attacker can send a transaction with as little as 1 wei, change the hash, and then front‑run a legitimate transaction that later calls validateLien. The validateLien check compares the current hash with the expected value, so the altered hash makes the check fail and the subsequent transaction reverts. This pattern can be repeated to block normal users from executing any function that relies on validateLien, such as auctionBuyNft, startLoanAuction, stopLoanAuction, and other loan‑related operations. From a user perspective the symptom is that a bid, auction start, or auction stop appears to fail with no obvious reason, often reverting with a generic error and leaving the user with no received NFT or loan progress. The impact is a loss of functionality rather than direct loss of funds, but it effectively freezes the protocol’s core workflows and can be used to harass participants or manipulate market outcomes. The condition occurs whenever an attacker can submit an addCredit transaction before a legitimate user’s transaction, which is feasible because the function lacks access control and accepts any msg.value, making it cheap to spam the network. The issue was discovered during a security audit that examined the flow of lien validation and noticed that the hash‑based integrity check could be subverted by an uncontrolled state change. The problem is subtle because the addCredit function appears harmless and the small ether amount does not raise gas‑price alarms, so the denial of service can remain hidden until a user experiences unexpected reverts. To remediate the issue the addCredit function should be restricted to the borrower, a minimum msg.value should be enforced, and optionally a time‑based modification interval should be added to prevent rapid successive updates. These changes restore the integrity of the lien hash and ensure that only authorized parties can modify credit information, eliminating the front‑run vector that leads to denial of service.

## Proof of Concept
`addCredit()` can be called by anyone, and the `msg.value` is as small as `1 wei`.

Users can modify Lien at a small cost, causing the value stored in `liens[lienId]=keccak256(abi.encode(lien))` to change. By front-run, the normal user’s transaction `validateLien()` fails the check, thus preventing the user’s transaction from being executed.

The following methods will be exploited (most methods with `validateLien()` will be affected). For example:

  1. Front-run `auctionBuyNft()` is used to prevent others from bidding.
  2. Front-run `startLoanAuction()` to prevent the lender from starting the auction.
  3. Front-run `stopLoanAuction()` is used to stop Lender from closing the auction.   
etc.

## Recommendation
1. `addCredit()` can execute only by the borrower.
   2. Add the modification interval period.
   3. Limit min of `msg.value`.
