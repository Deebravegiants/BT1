# [M] There is no slippage check in the `nuke

## Summary
Severity: Medium
Contest weight: 0.5404
Dataset id: 21812
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is a missing slippage or minimum‑claim check in the contract function that distributes ETH to NFT owners when they invoke the nuke() operation. The function computes the amount a caller can receive by multiplying the current fund balance by a per‑token nuke factor and then subtracts that amount from the shared pool. Because the calculation uses the live fund value without enforcing a lower bound, a later transaction can consume a large portion of the pool before an earlier‑submitted transaction is executed, causing the earlier caller to receive only a fraction of the amount they expected. This situation arises from the root cause that the contract does not lock the fund amount at the moment a claim is initiated and does not verify that the resulting claim meets a minimum threshold. An attacker, or simply the natural nondeterministic ordering of transactions in the sequencer, can submit a competing nuke() call that is processed first; the first call drains a substantial part of the pool, and the second call, which may have been submitted earlier, ends up receiving a reduced payout (for example, a user expecting 5 ETH receives only 2.5 ETH). The impact is a financial loss for the affected NFT holder, who sees a smaller balance transferred to their address, potentially losing up to 50 % of the anticipated reward. The issue manifests whenever multiple NFT owners try to claim from the same fund in a short time window, especially when the fund size is limited and the nuke factor is high. It affects all participants who hold claim‑eligible NFTs, undermines the protocol’s fairness guarantees, and can erode user trust because the UI will show a successful claim transaction but the received amount will be far lower than the displayed estimate. The problem was discovered during a manual audit that simulated two competing claims and observed the discrepancy in the received ETH. It can be hard to notice because the contract emits a successful claim event and the transaction does not revert; only a careful comparison of expected versus actual payouts reveals the shortfall. To remediate, the contract should introduce a minimum‑claim amount validation (a slippage guard) that reverts the transaction if the computed claim falls below a reasonable threshold, or alternatively snapshot the fund balance at the start of the claim and allocate a fixed share per token, thereby preventing later transactions from reducing earlier expectations. This class of bug is commonly known as a slippage or front‑running‑prone payout calculation flaw, where the lack of a guard allows ordering attacks to diminish user rewards.

## Proof of Concept
In the `nuke()` function, there is no minimum claim amount check. Consider the following scenario:

  1. The `fund` value of the `NukeFund` contract is 10 ETH.
  2. Alice is about to nuke an NFT with a nuke factor of 0.5, allowing her to receive 5 ETH.
  3. Bob also has an NFT with a nuke factor of 0.5 and calls the `nuke()` function with his NFT, front-running Alice.

     * Bob receives 5 ETH (see `L166`).
     * The remaining fund is now `10 ETH - 5 ETH = 5 ETH` (see `L174`).
  4. Next, Alice’s transaction is processed, and she receives only 2.5 ETH (0.5 of the remaining fund of 5 ETH).

If Alice’s transaction had been processed before Bob’s, she would have received 5 ETH. However, due to being front-run by Bob, she only receives 2.5 ETH, which is significantly less than expected. This highlights the necessity of implementing a minimum claim amount check in the `nuke()` function. With such a check, it is possible to prevent Alice from receiving only 2.5 ETH which is far below her expectations.

```solidity
function nuke(uint256 tokenId) public whenNotPaused nonReentrant {
  require(
    nftContract.isApprovedOrOwner(msg.sender, tokenId),
    'ERC721: caller is not token owner or approved'
  );
  require(
    nftContract.getApproved(tokenId) == address(this) ||
      nftContract.isApprovedForAll(msg.sender, address(this)),
    'Contract must be approved to transfer the NFT.'
  );
  require(canTokenBeNuked(tokenId), 'Token is not mature yet');

  uint256 finalNukeFactor = calculateNukeFactor(tokenId); // finalNukeFactor has 5 digits
  uint256 potentialClaimAmount = (fund * finalNukeFactor) / MAX_DENOMINATOR; // Calculate the potential claim amount based on the finalNukeFactor
  uint256 maxAllowedClaimAmount = fund / maxAllowedClaimDivisor; // Define a maximum allowed claim amount as 50% of the current fund size

  // Directly assign the value to claimAmount based on the condition, removing the redeclaration
  uint256 claimAmount = finalNukeFactor > nukeFactorMaxParam
    ? maxAllowedClaimAmount
    : potentialClaimAmount;

  fund -= claimAmount; // Deduct the claim amount from the fund

  nftContract.burn(tokenId); // Burn the token
  (bool success, ) = payable(msg.sender).call{ value: claimAmount }('');
  require(success, 'Failed to send Ether');

  emit Nuked(msg.sender, tokenId, claimAmount); // Emit the event with the actual claim amount
  emit FundBalanceUpdated(fund); // Update the fund balance
}
```

## Recommendation
It is recommended to implement a minimum claim amount check in the `nuke()` function.

Although base-chain has a private mempool, meaning MEV and Front-Running is not possible. There is a possibility of the mempool privacy changing, which will make this a valid issue. But it is impossible, now, judges can decide what they want to do with this. But possibility of mempool going public means this is still a risk.

Valid issue.

Reasoning:

  * Even without intentional front-running, transaction ordering can still have impacts similar to front-running. 
  * While users can’t see other pending transactions, market conditions can still change between transaction submission and execution
  * As far as I know, Transactions on Base are generally ordered on a first-come, first-served basis by the sequencer. Since, there is no guarantee that the first submitted TX will be processed first (due to multiple factors including network latency), the risk still exists.

I think this should downgraded to medium or QA for the same reasoning as described in [Issue #166](https://github.com/code-423n4/2024-07-traitforge-findings/issues/166):

  1. The mempool is private meaning the probability is extremely low.
  2. Front-running issues will always exist and it’s the same reasoning as with the auctions: “If I front-run you, you will have to pay the bigger price”. I guess it’s just the nature of the game.
  3. This certainly has a risk but the problem is that the game allows “the fastest” to win and let’s say the suggested mitigation is introduced and Alice gets `minNukeAmount`. Her tx will revert multiple times before that due to deviation from `minNukeAmount` and it’s not likely that she will get a much bigger amount as the competition will be extremely high for such amounts of ETH. There will be just the same situation if she was front-runned with the absence of slippage. The example with 2.5 ETH and 5 ETH seems highly unrealistic, as such amounts from `NukeFund` in real scenario will be taken almost right away.

@ABAIKUNANBAEV - You are mistaking two things:

  1. The slippage here is different from #166. The slippage here can cause significant loss for users (up to 50% of what they expected) as outlined by the PoC: the user received 2.5 ETH instead of 5 ETH, we are talking about a 2.5 ETH difference which is about `$6k`.
  2. There doesn’t have to be front-running for this issue to happen as explained in another duplicate [Issue #753](https://github.com/code-423n4/2024-07-traitforge-findings/issues/753), the warden incorrectly mentioned this in his report.

If Alice submits her transaction before Bob, according to the _fastest rule_ , Alice’s transaction should be executed first. But still, Bob’s transaction can be executed before Alice due to several reasons like network congestion, etc.; something that players can not control.

Yes, and as I outlined, such `minAmount` mitigation for this issue is senseless as, at the start of the game, everybody will try to claim and here “the fastest wins” rule comes into play. The fastest here will get the most amount of money. You make a logical mistake by saying that users here “lose the funds” as they don’t lose anything - they only own a `tokenId` that makes them eligible to claim at most 50% of the funds. By saying they lose funds - they didn’t lose, they just did not get amount that they could potentially get - big difference. I personally think it’s at most QA.

I disagree that users don’t lose the funds. If they don’t receive what they expect, they have burned their NFT with which later on they can claim what they desire. There is definitely a loss of funds, as you have to pay for the NFT; either mint it, forge it or buy it on an open market. 

They don’t own any funds to lose them, it’s just opportunity for everybody.

I believe it is fair to downgrade it to Medium for similar reasons explained [here](https://github.com/code-423n4/2024-07-traitforge-findings/issues/166#issuecomment-2306770957).
