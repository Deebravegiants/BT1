The user is asking to find an analog to a reported vulnerability where price feeds are not validated for staleness, leading to incorrect value calculations. The original report highlights `CompoundConnector.sol`'s reliance on `comet.getPrice()`, which only checks for non-zero positive prices but not staleness.

I found several instances in the `AuditingProject/AllProjects` repository that discuss or exhibit similar vulnerabilities related to oracle price staleness and validation.

### Title
Improper price validation in `StaderOracle.sol` will lead to stale prices being used - ([Project: staderforeth] [File: ethx/contracts/StaderOracle.sol])

### Summary
The `StaderOracle.sol` contract in the `staderforeth` project discards the `updatedAt` timestamp from Chainlink price feeds, leading to a lack of staleness checks. This allows stale price data to be used for critical exchange rate calculations, which can be manipulated by an unprivileged attacker.

### Finding Description
The `getPORFeedData()` function in `StaderOracle.sol` retrieves price data from Chainlink aggregators but discards the `updatedAt` and `answeredInRound` values.  This means there is no check for the staleness of the price feed. Additionally, the `block.number` is returned as the reporting block instead of the feed's `updatedAt`, which can make stale data appear current.  The `updateERFromPORFeed()` function, which consumes this data, is permissionless, allowing any address to update the protocol's ETHx exchange rate using potentially stale information. 

### Impact Explanation
The use of stale price data directly impacts the ETHx exchange rate, which governs minting and redeeming prices. An attacker could repeatedly push stale-but-in-band prices, leading to arbitrage opportunities where ETHx can be minted cheaply or redeemed richly.  This results in incorrect accounting and potential financial loss for the protocol.

### Likelihood Explanation
The likelihood is high because the `updateERFromPORFeed()` function is permissionless, meaning any external caller can trigger the update with stale data.  The absence of staleness checks makes the system vulnerable to price manipulation whenever the Chainlink feed lags.

### Recommendation
Implement proper staleness checks by utilizing the `updatedAt` timestamp returned from `latestRoundData()`. Ensure that the price data is recent before using it to update critical protocol parameters like the exchange rate. Additionally, consider adding checks for `answeredInRound` to ensure the round is complete.

### Proof of Concept
An attacker can observe a lag in the Chainlink price feed for `totalETHBalanceInInt` or `totalETHXSupplyInInt`.
1. The attacker calls `updateERFromPORFeed()` when the Chainlink feed is stale but within the `erChangeLimit`. 
2. The `getPORFeedData()` function fetches the stale price data, as it does not validate `updatedAt`. 
3. The `updateWithInLimitER()` function is called with this stale data, updating the ETHx exchange rate to a value that does not reflect the current market price. 
4. The attacker can then exploit this stale exchange rate for profit by minting or redeeming ETHx at an advantageous price. 

## Notes
The `issues.md` file also mentions other instances of oracle validation issues, such as `F-18` and `F-19`, which relate to `latestRoundData` with no staleness/sign check.  Specifically, `F-18` discusses out-of-scope oracles in `listadao` that skip checks, while in-scope oracles delegate to `ResilientOracle` which performs validation.   `F-19` in `velvetcapital` highlights an incomplete sign check (`price == 0` instead of `price <= 0`) but notes that staleness is handled correctly.   Another relevant finding, `F-37` in `listadao`, describes an unchecked `int256 -> uint256` cast on a price with only staleness checked, but not positivity.  The `StaderOracle.sol` case (`F-31`) is the most direct analog as it explicitly discards `updatedAt` and `answeredInRound`, leading to stale price usage in a permissionless context.  

View this search on DeepWiki: https://deepwiki.com/search/-analog-scan-prompt-external-r_39497b21-9406-43dc-9d25-ddd28e0505dc
