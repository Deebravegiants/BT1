# [H] H-03 | Execution Of Orders Can Be Skipped

## Summary
Severity: High
Contest weight: 0.2361
Dataset id: 2411
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Executable orders can get skipped in certain cases. Let's say we are at tick 0 and we have a limit order at 120-180 range isToken0: true. If we make a swap zeroForOne: false then we will move the price up. If the price happens to land somewhere between 120-180 the limit orders will not execute. The issue appears when when we make another such swap then beforeSwapTick is going to be between 120-180 and the afterSwapTick is going to be after 180. The limit orders will not execute again. This limit orders will get executed if the beforeSwapTick is before 120 and the afterSwapTick is more than 180. In reality the price have already passed the limit order range and should have been executed already. In the current implementation and example the bottom tick gets compared to the beforeSwapTick during the binary search and this causes the orders to get skipped.

## Proof of Concept
https://gist.github.com/fatherGoose1/9f78fa83693323df7778d59244cafaf6

## Recommendation
Consider modifying _findOverlappingPositions to select positions that the price range have already passed, despite the beforeSwapTick value.
