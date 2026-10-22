# [H] `twTAP.participate` can be exploited to permanently freeze the NFT contract

## Summary
Severity: High
Contest weight: 0.4842
Dataset id: 19070
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`twTAP` is a omnichain NFT (ONFT721) that will be deployed on all supported chains.

However, there are no access control for operations meant for execution on the host chain only, such as `participate()`, which mints `twTAP`.

The implication of not restricting `participate()` to host chain is that an attacker can lock `TAP` and participate on other chain to mint `twTAP` with a tokenId that does not exist on the host chain yet. The attacker can then send that `twTAP` to the host chain using the inherited `sendFrom()`, to permanently freeze the `twTAP` contract as `participate()` will fail when attempting to mint an existing `tokenId`.

It is important to restrict minting to the host chain so that `mintedTWTap` (which keeps track of last minted tokenId) is only incremented at one chain, to prevent duplicate tokenId. That is because the `twTAP` contracts on each chain have their own `mintedTWTap` variable and there is no mechanism to sync them.

## Proof of Concept
Consider the following scenario,

1. Suppose we start with `twTAP.mintedTwTap == 0` on all the chains, so next tokenId will be `1`.
2. Attacker `participate()` with 1 TAP and mint `twTAP` on a non-host chain with `tokenId` `1`.
3. Attacker sends the minted `twTAP` across to host chain using `twTAP.sendFrom()` to permanently freeze the `twTAP` contract.
4. On the host chain, the `twTAP` contract receives the cross chain message and mint a `twTAP` with `tokenId` `1` to attacker as it does not exist on host chain yet. (Note this cross-chain transfer is part of Layer Zero ONFT721 mechanism)
5. Now on the host chain, we have a `twTAP` with `tokenId` `1` but `mintedTwTap` is still `0`. That means when users try to `participate()` on the host chain, it will try to mint a `twTAP` with `tokenId` `1`, and that will fail as it now exists on the host chain. At this point `participate()` will be permanently DoS, affecting governance and causing loss of rewards.
6. Note that the attacker can then transfer the `twTAP` back to the source chain and exit position to retrieve the locked `TAP` token. However, the host chain still remain frozen as the owner of `tokenId` `1` will now be `twTAP` contract itself after the cross chain transfer.

Note that the attack is still possible even when `mintedTwTap > 0` on host chain as attacker just have to repeatedly mint on the non-host chain till it obtains the required `tokenId`.

## Recommendation
Add in access control to prevent host-chain-only operations such as `participate()` from being executed on other chains.
