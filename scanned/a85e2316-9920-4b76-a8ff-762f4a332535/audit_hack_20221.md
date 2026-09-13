# [H] 5.2.2 depositandwithdrawfunctions are susceptible to sandwich attacks

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** AeraVaultV1.sol#L402-L453, AeraVaultV1.sol#L456-L
**Description:** Transactions calling thedeposit()function are susceptible to sandwich attacks where an attacker
can extract value from deposits. A similar issue exists in thewithdraw()function but the minimum check on the
pool holdings limits the attack’s impact.
Consider the following scenario (swap fees ignored for simplicity):

1. Suppose the Balancer pool contains two tokens, WETH and DAI, and weights are 0.5 and 0.5. Currently,
    there is 1WETHand 3kDAIin the pool andWETHspot price is 3k.
2. The Treasury wants to add another 3kDAIinto the Aera vault, so it calls thedeposit()function.
3. The attacker front-runs the Treasury’s transaction. They swap 3kDAIinto the Balancer pool and get out 0.
    WETH. The weights remain 0.5 and 0.5, but becauseWETHandDAIbalances become 0.5 and 6k,WETH’s spot
    price now becomes 12k.
4. Now, the Treasury’s transaction adds 3kDAIinto the Balancer pool and upgrades the weights to 0.5*1.5: 0.
    = 0.6: 0.4.
5. The attacker back-runs the transaction and swaps the 0.5WETHthey got in step 3 back toDAI(and recovers
    theWETH’s spot price to near but above 3k). According to the current weights, they can get 9k*(1 - 1/r) = 3.33k
    DAIfrom the pool, where r = (2ˆ0.4)ˆ(1/0.6).
6. As a result the attacker profits 3.33k - 3k = 0.33kDAI.
**Recommendation:** Potential mitigations include:
- Adopting a two-step deposit and withdraw model. First, disable trading and check that the pool’s spot price is
within range. If not, enable trading again and let arbitragers re-balance the pool. Once rebalanced, deposit
or withdraw from the pool. Then enable trading again (possibly with weights).
- Avoid depositing or withdrawing if the pool balance has changed in the same block. ThelastChangeBlock
variable stores the last block number where the pool balance was modified. By ensuringlastChangeBlock
is less than the current block number, same-block sandwich attacks can be prevented. Still, this mitigation
does not avoid multi-block MEV attacks.
- Similar to slippage protection, add price boundaries as parameters to thedeposit()andwithdraw()func-
tions to ensure pool’s spot price is within boundaries before and after deposit or withdrawal. Revert the
transaction if boundaries are not met.
- Use Flashbots to reduce sandwiching probabilities.
**Gauntlet:** As discussed, this is a problem with spot price agnostic depositing into an AMM. V2 will introduce
oracle-informed spot price updates. We will take the following actions for V1:
- Advise treasuries against making large deposits
- For sensitive/larger deposits, offer an option to reject the transaction if balances have been changed in the
block (lastChangeBlock), implemented in PR #138.
- Advise treasuries to use flash bots when possible
**Spearbit:** Actions taken on a procedural and not technical level.
