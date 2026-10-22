# [C] Insuﬃcient Permissions Granted to New Auctions

## Summary
Severity: Critical
Contest weight: 0.5273
Dataset id: 14654
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a missing role assignment when a new auction is reopened through the TermRepoCollateralManager contract. Specifically, the function that reopens an auction does not grant the AUCTION_LOCKER permission to the newly created auction contract. The AUCTION_LOCKER role is required for the auction to execute its lock‑and‑settle logic, which includes finalizing bids, releasing collateral, and distributing rewards. Because the role is not granted, the auction contract lacks the authority to call the internal lock function, causing the auction to remain in an unfinished state indefinitely. This situation can be triggered whenever the protocol attempts to reopen a previously closed auction or create a fresh auction instance; the condition occurs under normal operational flow, not only under malicious input. Users who participate in the auction expect their bids to be processed and their collateral to be returned after the auction ends, but instead they observe that the auction never reaches the settlement step, their balances appear unchanged, and any pending refunds are missing. The impact is a denial‑of‑service on the auction mechanism, effectively locking user funds and breaking the economic guarantees of the protocol. The issue was discovered during a security audit that reviewed role‑based access control patterns and identified that the reopenToNewAuction function omitted a call to _grantRole for AUCTION_LOCKER. The bug is subtle because the contract compiles and runs without reverting; the failure manifests only as a silent stall, making it hard to detect without inspecting role assignments or observing that auctions never complete. To remediate, the contract should explicitly grant the AUCTION_LOCKER role to the auction address when reopening, ensuring the auction contract can perform its lock and settlement steps. This aligns the implementation with the intended permission model and restores the ability for auctions to finalize and release funds.

## Recommendation
Grant AUCTION_LOCKER permissions to a new auction in TermRepoCollateralManager.reopenToNewAuction(), such as:
```solidity
function reopenToNewAuction(TermAuctionGroup calldata termAuctionGroup)
    external
    onlyRole(DEFAULT_ADMIN_ROLE)
{
    _grantRole(
        AUCTION_LOCKER,
        address(termAuctionGroup.auction)
    );
}
```
