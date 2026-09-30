# [M] Visor Finance incident: Uniswap V3 liquidity management protocol Visor Finance was hacked again. Hackers took advantage of the loopholes to withdraw more

## Summary
Severity: Medium
Target: Visor Finance
Loss: 120 ETH
Attack method: Contract Vulnerability
Published: 2021-12-22
Source: https://medium.com/visorfinance/post-mortem-for-vvisr-staking-contract-exploit-and-upcoming-migration-7920e1dee55a
Type: slowmist-incident

## Details
Uniswap V3 liquidity management protocol Visor Finance was hacked again. Hackers took advantage of the loopholes to withdraw more than 8.8 million VISRs and sold them on Uniswap, causing the VISR tokens to plummet by nearly 95% and profit over 120 ETH through Tornado Cash. Money laundering. According to SlowMist analysis, this attack is due to a flaw in the RewardsHypervisor contract when checking the permissions of the user's recharge, causing the attacker to construct a malicious contract to arbitrarily cast mortgage credentials. Prior to this June, Visor Finance was also hacked and lost more than US$500,000.
