# [M] Curve LlamaLend incident: On March 2, 2026, Curve Finance’s LlamaLend sDOLA/crvUSD market suffered a flash-loan + donation attack. The attacker first used a

## Summary
Severity: Medium
Target: Curve LlamaLend
Loss: $ 240,000
Attack method: Donation Attack
Published: 2026-03-02
Source: https://x.com/CurveFinance/status/2032917563051553092
Type: slowmist-incident

## Details
On March 2, 2026, Curve Finance’s LlamaLend sDOLA/crvUSD market suffered a flash-loan + donation attack. The attacker first used a massive LLAMMA exchange to push all positions into soft liquidation, then inflated the sDOLA oracle price by 13.79% (1.189 → 1.353) via DolaSavings.stake() donation. This hard-liquidated 27 borrowers (~$10.9M debt). Attacker profited ~$240K; borrowers lost ~$822K equity (Curve DAO later proposed full compensation). Lenders and core protocol unaffected.
