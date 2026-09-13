# [M] MT-WBNB liquidity pool incident: According to BlockSec Phalcon's monitoring, a suspicious transaction targeting the MT-WBNB liquidity pool on BSC was detected seve

## Summary
Severity: Medium
Target: MT-WBNB liquidity pool
Loss: $ 242,000
Attack method: Reserve Manipulation Attack
Published: 2026-03-10
Source: https://x.com/phalcon_xyz/status/2031226066572837313?s=46
Type: slowmist-incident

## Details
According to BlockSec Phalcon's monitoring, a suspicious transaction targeting the MT-WBNB liquidity pool on BSC was detected several hours ago, resulting in an estimated loss of approximately $242,000. The root cause lies in a flaw within the buyer restriction mechanism: under deflationary mode, normal buy orders were reverted; however, the router and pair addresses were whitelisted. The attacker bypassed these restrictions by swapping and removing liquidity through the router to acquire MT tokens from the pair. Subsequently, the attacker sold MT to accumulate a pendingBurnAmount and invoked the distributeFees() function to directly burn MT from the trading pair, artificially inflating the price. This allowed the attacker to swap MT back for WBNB to realize a profit. Furthermore, a referral rule that allowed the transfer of the first 0.2 MT to bypass buyer restrictions enabled the attacker to initiate the exploit.
