# [M] Decimals not Required in the Deposit Function

## Summary
Severity: Medium
Contest weight: 0.1586
Dataset id: 8807
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of allowing users to specify decimal fractions when depositing tokens into a game where wagers are defined as whole units. The contract does not enforce integer‑only deposits, so a user can send 1.5 tokens. Because the backend assumes fixed wager amounts and performs integer arithmetic for accounting, the presence of fractional values can cause rounding mismatches when the session balance is later used for rollup or withdrawal calculations. An attacker could exploit this by depositing a fractional amount that, after rounding, results in a lower effective wager while still being credited with a full wager slot, effectively gaining a free fraction of a token. Conversely, rounding down could cause the contract to think the user has insufficient balance, leading to rejected withdrawals or loss of funds. The issue manifests whenever the deposit function accepts a value with a non‑zero decimal part; it is triggered during normal gameplay when a player initiates a session and supplies a custom amount. All participants who can interact with the deposit endpoint are affected, including regular users and the protocol’s accounting logic. The flaw was discovered during a manual UI/UX audit that observed that the deposit input field accepted decimal numbers despite the protocol’s documentation stating that wagers are whole numbers. Because the contract does not explicitly reject fractions, the problem can be subtle: the UI may display a fractional balance, but the backend may truncate or round it silently, making the discrepancy hard to notice until a withdrawal fails or the accounting totals become inconsistent. The vulnerability belongs to the class of input‑validation and rounding errors, where unchecked numeric precision leads to accounting drift. To remediate, the deposit function should enforce that the amount is an integer multiple of the token’s smallest unit (e.g., require amount % 1 == 0 or use token decimals to validate) and reject any value containing a fractional component. This prevents rounding anomalies and aligns the on‑chain accounting with the protocol’s business rule that wagers are fixed, whole‑number amounts.

## Proof of Concept
When a user initiates a game and proceeds to deposit, it is possible to enter amounts with decimals.

Figure 3: In the image: The application processes decimals in the Session Balance.  
Figure 4: In the image: The application processes decimals in the Session Balance.  
Although the application seems to manage calculations involving decimal numbers in the rollup/withdrawal process, allowing users to input decimal numbers is unnecessary. This is because the application enforces a fixed wager amount for each available token. Leaving the decimals might cause rounding issues in the backend, in this way the input must be properly constrained.

## Recommendation
Consider restricting users from entering decimal amounts when making deposits.
