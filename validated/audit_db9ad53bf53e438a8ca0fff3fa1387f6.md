This query describes a critical vulnerability where a liquidation function reverts due to an underflow error when a position is liquidatable, making it impossible to liquidate. This occurs because the condition that makes a position liquidatable also causes an arithmetic underflow during the liquidation process.

The provided codebase context, specifically `AuditingProject/AllProjects/issues.md`, contains a section on "Systematic scan record, round 15 â liquidation incentive vs available collateral (bad debt): clean" . This section discusses a similar class of vulnerability where a liquidation might become impossible or lead to bad debt.

### Finding Description

The external report describes a scenario where the `attemptLiquidation()` function in a `TradableMarginHandler` contract reverts if a position is liquidatable. This is due to an accounting underflow error when calculating `user_reserveBalance += marginBalance + collateralAmount - totalAmountOwed;` if `marginBalance + (collateralAmount - protocolPercentOfCollateral) <= tradingFeesAccumulated` . This condition, which indicates a position is liquidatable, simultaneously causes the liquidation transaction to fail.

### Impact Explanation

If such a vulnerability exists in any project within the `AllProjects` repository, it would lead to positions becoming unliquidatable. This could result in bad debt accumulating within the protocol, as the protocol would be unable to recover funds from undercollateralized positions. This directly impacts the solvency and stability of the protocol.

### Likelihood Explanation

The `issues.md` file indicates that a systematic scan for "liquidation incentive vs available collateral (bad debt)" was performed . This scan specifically looked for liquidation functions that apply a bonus/incentive without capping it at the borrower's actual collateral, which could lead to unliquidatable positions or over-payment to liquidators .

The scan found several hits, including in `fluxfinance` and `justlenddao` within their `liquidateCalculateSeizeTokens` function . These were identified as Compound V2 forks where `seizeTokens` is computed without a clamp in the calculator . While the bound is enforced one layer down in `seizeInternal` to prevent over-seizure, it results in deeply underwater positions becoming **unliquidatable** . This is described as inherent Compound V2 behavior rather than a fork-introduced defect .

Therefore, the likelihood of finding a similar issue (unliquidatable positions due to arithmetic constraints) in Compound V2 forks within the `AllProjects` repository is high, as it's a known behavior of that codebase.

### Recommendation

The external report recommends using `int` instead of `uint` to allow for negative values or checking if the increment to `user_reserveBalance` is positive or negative and performing addition or subtraction accordingly . Additionally, a liquidation scenario similar to this one should be included in tests .

For projects that are Compound V2 forks, addressing the inherent unliquidatable state for deeply underwater positions would require modifying the liquidation logic to handle such scenarios gracefully, potentially by allowing partial liquidations or specific bad-debt write-off mechanisms.

### Proof of Concept

While no direct analog with the exact underflow condition described in the prompt was found, the `issues.md` file highlights a similar outcome in Compound V2 forks:

In `fluxfinance` and `justlenddao`, the `liquidateCalculateSeizeTokens` function calculates the amount of tokens to seize without an upper bound based on available collateral . Although `seizeInternal` prevents over-seizure by reverting on underflow if `borrowerTokensNew = borrowerTokens - seizeTokens` would be negative, this effectively makes deeply underwater positions unliquidatable . This behavior, while different in root cause (underflow on subtraction vs. underflow on addition after subtraction), leads to the same critical impact: positions cannot be liquidated.

This can be triggered by an unprivileged user attempting to liquidate a deeply underwater position in a Compound V2 fork within the `AllProjects` repository. The `liquidate` function would revert, preventing the liquidation.

## Notes

The `issues.md` file provides a high-level overview of systematic scans performed across the `AllProjects` repository. While it identifies a class of issues related to unliquidatable positions in Compound V2 forks, it does not provide specific file paths or line numbers for those projects. To confirm the exact analog and provide a precise proof of concept, a deeper dive into the code of `fluxfinance` and `justlenddao` (or any other Compound V2 fork within the repository) would be necessary. The provided context only indicates the *existence* of such a class of issues and their general behavior.

View this search on DeepWiki: https://deepwiki.com/search/-analog-scan-prompt-external-r_d1b642ed-0e1b-42f5-8207-23f2044abb4e
