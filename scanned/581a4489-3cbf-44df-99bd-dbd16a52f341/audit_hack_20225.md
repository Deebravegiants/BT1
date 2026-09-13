# [M] 5.3.2 Front-running attacks onfinalizecould affect received token amounts

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** AeraVaultV1.sol#L539, AeraVaultV1.sol#L899-L
**Description:** ThereturnFunds()function (called byfinalize()) withdraws the entire holdings in the Balancer
pool but does not allow the caller to specify and enforce the minimum amount of received tokens. Without such
check thefinalize()function could be susceptible to a front-running attack.
A potential exploit scenario looks as follows:

1. The notice period has passed and the Treasury callsfinalize()on the Aera vault. Assume the Balancer
    pool contains 1WETHand 3000DAI, and thatWETHandDAIweights are both 0.5.
2. An attacker front-runs the Treasury’s transaction and swaps in 3000DAIto get 0.5WETHfrom the pool.
3. As an unexpected result, the Treasury receives 0.5WETHand 6000DAI. Therefore an attacker can force the
    Treasury to accept the trade that they offer.
Although the Treasury can execute a reverse trade on another market to recover the token amount and distribution,
not every Treasury can execute such trade (e.g., if a timelock controls it). Notice that the attacker may not profit from
the swap because of slippage but they could be incentivized to perform such an attack if it causes considerable
damage to the Treasury.
**Recommendation:** Possible mitigations include:
- Allowing the caller to specify the minimum amount of each token and revert the transaction if not enough
tokens are available.
- Adopting a two-step finalization pattern. First, disable trading and check if the token amounts in the Balancer
pool are as desired. If not, enable trading again and let arbitragers re-balance the pool. Once rebalanced,
finalize the vault.
- Use Flashbots to reduce front-running probabilities.
**Gauntlet:** Based on our latest thinking, trading should be paused wheninitiateFinalizationis run. That
should resolve this issue.
**Spearbit:** setSwapEnabled(false)has been added ininitiateFinalization()in PR #137. It is worth not-
ing that pausing trading does not completely solve the issue. IfinitiateFinalization()happens to be front
run (although not profitable for a frontrunner, it could still happen), then the token distributions could still be off.
This situation should probably be detected (manually?) and corrected withenableTradingWithWeights()and
disableTrading().
**Gauntlet:** I think there are 2 things that are important:
- If the treasury is using withdraw and asking for a specific amount of tokens, that they don’t get less than that.
If there happens to be a front-running transaction, just like in an AMM they may not be able to withdraw what
they want
- If the treasury is finalizing they should expect to retain a decent amount of the **value** of the pool, but since
it’s a liquidity share in an AMM, there aren’t guarantees about the specific ratios of token amounts. The only
guarantee is the relationship between token weights, balances and spot prices.
**Spearbit:** The value indeed stays the same. Only if the token distribution would be important you would want to
solve this.


Assuming the token distribution doesn’t matter then you might as well keep the code as is (unless there are other
reasons to change).
[e.g frontrun ofinitiateFinalization()+ trade pause has the same effect as frontrun offinalize()while trade
hasn’t been paused ]
**Gauntlet:** I still like the proposal as we see other benefits in pausing trading. Since trading is primarily a means of
rebalancing execution, we can shut it off post initiation of finalization to mitigate impermanent loss for the treasury.
**Spearbit:** Acknowledged. Beware thatenableTradingWithWeights(),enableTradingRiskingArbitrage()and
disableTrading()still work afterinitiateFinalization(). This could be put to good use but also unwanted (in
that case additional checks are required in these functions).
