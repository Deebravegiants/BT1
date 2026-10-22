# [C] Euler Finance incident: The DeFi lending protocol Euler Finance was attacked, and the attackers made a profit of about 197 million US dollars. The attacke

## Summary
Severity: Critical
Target: Euler Finance
Loss: $ 197,000,000
Attack method: Flash Loan Attack
Published: 2023-03-13
Source: https://twitter.com/SlowMist_Team/status/1635288963580825606
Type: slowmist-incident

## Details
The DeFi lending protocol Euler Finance was attacked, and the attackers made a profit of about 197 million US dollars. The attacker used flashloans to deposit funds and then leveraged them twice to trigger the liquidation logic, donating the funds to the reserve address and conducting a self-liquidation to collect any remaining assets. Two key factors contributed to the success of the attack: 1. Funds were donated to the reserved address without being subjected to a liquidity check. This created a mechanism that could directly trigger soft liquidation. 2. When the soft liquidation logic was triggered by high leverage, the yield value increased, enabling the liquidator to obtain most of the collateral funds from the liquidated user's account by transferring only a portion of the liabilities to themselves. Given that the value of the collateral funds exceeded the value of the liabilities (which were only partially transferred due to the soft liquidation), the liquidator was able to successfully pass their health factor check (checkLiquidity) and withdraw the obtained funds. On April 4th, Euler Labs tweeted that after a successful negotiation, the attacker has returned all the funds stolen from the agreement on March 13th, because the attacker has returned the funds, the $1 million reward campaign launched by the foundation No new information will be accepted.
