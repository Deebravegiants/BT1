# [M] MONA incident: On April 14, 2026, attackers exploited the BurnAddress mechanism in the MONA token on BSC via a Deferred LP Burn / reserve manipul

## Summary
Severity: Medium
Target: MONA
Loss: $ 60,950
Attack method: Reserve Manipulation Attack
Published: 2026-04-13
Source: https://www.darknavy.org/web3/exploits/burnaddress-mona-deferred-lp-burn/
Type: slowmist-incident

## Details
On April 14, 2026, attackers exploited the BurnAddress mechanism in the MONA token on BSC via a Deferred LP Burn / reserve manipulation attack. The attacker first farmed 10,000 MONA through 25 fresh accounts, sold 9,900 MONA to create a deferred burn credit, bought out most of the pool's MONA inventory, then triggered BurnAddress.burn() with a zero-value transferFrom to burn MONA directly from the LP and call sync(). This left the MONA/USDT pair with near-zero MONA but almost full USDT reserves. Finally, selling the remaining ~100 MONA drained a large amount of USDT. Flash loans from Moolah and borrowing from Venus were used for funding and fully repaid in the same transaction. The root cause was non-atomic handling in _handleSell() and burnsellMona(): USDT payout happened immediately while MONA burn was deferred and could be triggered later, breaking the AMM invariant.
