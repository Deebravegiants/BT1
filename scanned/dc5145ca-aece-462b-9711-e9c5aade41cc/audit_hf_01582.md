# [H] MJR-4 Uncounted fees in USDT

## Summary
Severity: High
Contest weight: 0.0140
Dataset id: 8474
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability originates from the contract’s reliance on the ERC‑20 transferFrom function to move an exact amount of USDT from a user to the protocol, while USDT implements a fee‑on‑transfer mechanism that reduces the amount actually received. Because the contract does not account for this fee, it may end up holding fewer tokens than the amountIn parameter supplied by the caller. This discrepancy can occur whenever openCreditAccount invokes transferFrom on USDT, which is expected to credit the contract with the full requested amount. The root cause is the assumption that transferFrom will always transfer the precise value, an assumption that holds for standard ERC‑20 tokens but not for fee‑on‑transfer tokens such as USDT. An attacker or any user can trigger the condition simply by depositing USDT, causing the contract to believe it has sufficient collateral while the real balance is lower. The impact includes failed credit‑account openings, potential under‑collateralisation of leveraged positions, and unexpected reverts or loss of funds for users who expect their full deposit to be usable. From the user’s perspective the UI may show that the deposit was accepted, but later actions (e.g., opening a leveraged position) revert or result in zero usable balance, leading to confusion when “my funds disappeared” or “the refund is missing”. The issue was discovered during a manual audit when the auditors observed that the contract’s balance after a transferFrom call was consistently lower than the amount requested, a symptom that is easy to miss because the transferFrom call returns true and does not revert. Detecting the problem requires checking the actual token balance after the transfer, which the current implementation omits. To remediate, the protocol should either query the contract’s USDT balance after the transfer and use that value when opening a credit account, or adjust the amountIn to include the expected fee, or restrict usage to fee‑free tokens. Conceptually, the bug belongs to the class of “fee‑on‑transfer token handling errors”, where accounting assumptions about token transfers are violated, leading to mismatched accounting and potential financial loss.

## Recommendation
We recommend to call openCreditAccount with current contract balance.
