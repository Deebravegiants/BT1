# [C] C-1 StUSR Inﬂation Attack

## Summary
Severity: Critical
Contest weight: 0.6595
Dataset id: 14151
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
• ERC20RebasingUpgradeable.sol#L386-L398
```
The empty StUSR pool is vulnerable to an Inflation Attack despite having some protective measures, which can lead to the loss of funds for early depositors to the benefit of a hacker, as well as causing a DOS (Denial of Service).
StUSR has two protection mechanisms against an Inflation Attack:
1. A depositor cannot receive 0 shares.
2. The exchange rate is calculated with 1 virtual share and 1 virtual asset.
In practice, 1 virtual share is not sufficient to protect against a profitable attack.

## Proof of Concept
1. Before an attack, the pool has 0 shares and 0 assets.
2. The hacker mints 1000 wei shares. Now the pool has 1000 wei shares plus 1 virtual share.
3. The hacker directly transfers 1,001,000 USR - 1001 wei into the StUSR pool. At this point, the hacker holds 1000 shares worth 1000 USR each, while losing 1000 USR to the pool's 1 virtual share.
4. The first victim deposits 1999 USR and receives shares = 1999e18 * 1001 / 1001000e18 = 1 wei. The value of 1 share is now approximately 1001 USR. The victim loses about 1000 USR, which is distributed to the pool. Since the hacker owns 99.8% of the pool, most of the profit goes to the hacker. At this point, the hacker has almost recovered the cost of the attack.
5. The second victim deposits 1999 USR and receives shares = 1999e18 * (1001 + 1) / (1002999e18 + 1) = 1 wei. The value of 1 share is now approximately 1002 USR. Again, the victim loses about 1000 USR, mostly to the hacker's benefit. At this point, the hacker is in profit.
State of the contract for each step:
1 wei Hacker's
Step totalShares()+1 _totalUnderlyingTokens()+1 share total profit
value (approx.)
1 0 0
2 1000 + 1 1000 + 1 1 wei 0
3 1000 + 1 1,001,000e18 1000 -1000 USD
USR
4 1001 + 1 1,002,999e18 ~1001 0
USR
5 1002 + 1 1,004,998e18 ~1002 +1000 USD
USR

## Recommendation
We recommend using 1000 virtual shares.
