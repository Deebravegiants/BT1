# [M] Stableswap - Deadline do not work

## Summary
Severity: Medium
Contest weight: 0.0982
Dataset id: 9980
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `ensure` modifier is commented, so deadlines will not work when passing orders, breaking this functionality.

The warden has shown how, due to a comment, the modifier `deadline` doesn’t work.

Because Front-running is a key aspect of AMM design, `deadline` is a useful tool to ensure that your tx cannot be “saved for later”.

Due to the removal of the check, it may be more profitable for a miner to deny the transaction from being mined until the transaction incurs the maximum amount of slippage.

The lack of deadline means that the tx can be withheld indefinitely at the advantage of the miner.

For those reasons I agree with Medium Severity.

## Recommendation
No recommendation
