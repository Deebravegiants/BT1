# [H] H-10 | Borrows In The Floor Invalidate Baseline Value

## Summary
Severity: High
Contest weight: 0.2351
Dataset id: 21463
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Upon borrowing reserves are transferred out of the floor position and are accounted for in the virtual reserves. When a borrow occurs within the floor position, the reserves removed from the floor will not contribute towards the floor liquidity, therefore not requiring additional reserves to enter the floor upon swaps which move the price upwards out of the floor.
As a result, when reserves are moved into the virtual reserves and price moves upwards out of the floor, the virtual floor reserves are increasingly stretched wider across the floor. As a result the virtual floor reserves offer a smaller amount of liquidity and capacity as the price increases.
This can lead to an invalidation of the capacity invariant of the system, which ultimately invalidates the baseline value of the bAsset.

## Recommendation
Implement validation in the _leverage function such that if the price were to rise to the upper tick of the floor and the capacity invariant would be invalidated, the borrow reverts. Be sure that this validation ignores any capacity gain that would come as a result of additional reserves in the Floor as price rises.
Additional reserves that would enter the floor as price increases must be ignored as they can mask an invalidation of the capacity invariant that would occur at an intermediate tick before the upper tick of the Floor.
