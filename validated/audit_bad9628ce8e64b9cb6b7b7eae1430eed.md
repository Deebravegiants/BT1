### Title
No Sequencer Uptime Check in Chainlink Oracle Allows Stale Price Exploitation on L2 - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

### Summary
`ChainlinkOracleForRSETHPoolCollateral.getRate()` queries a Chainlink price feed on L2 without checking the L2 sequencer uptime feed. During sequencer downtime, the Chainlink oracle on L2 cannot be updated, so it returns the last pre-downtime price. The existing staleness guard (`answeredInRound < roundID`) does not protect against this: when the sequencer is down, no new rounds are pushed, so `answeredInRound == roundID` still passes. An attacker can force-include transactions on Arbitrum (via the L1 inbox) during downtime to deposit collateral at a stale inflated price and extract more rsETH than the collateral is worth.

### Finding Description
`ChainlinkOracleForRSETHPoolCollateral` is the oracle used by the L2 pool contracts (`RSETHPool` on Arbitrum, `RSETHPoolNoWrapper` on Arbitrum/Unichain, and related variants) to price collateral tokens deposited by users. The `getRate()` function calls `AggregatorV3Interface(oracle).latestRoundData()` and applies three guards:

```solidity
if (answeredInRound < roundID) revert StalePrice();
if (timestamp == 0) revert IncompleteRound();
if (ethPrice <= 0) revert InvalidPrice();
```

None of these guards check the Chainlink L2 sequencer uptime feed. When the L2 sequencer is down:
- Chainlink oracle nodes cannot push new rounds to the L2 feed.
- `roundID` and `answeredInRound` remain equal (no new round), so `answeredInRound < roundID` is `false` — the `StalePrice` revert is never triggered.
- `timestamp` is non-zero (it is the timestamp of the last pre-downtime update).
- The price returned is the last price before the sequencer went down, which may be arbitrarily stale.

There is also no heartbeat/time-elapsed check (`block.timestamp - timestamp > HEARTBEAT`), compounding the staleness window.

The Chainlink-recommended pattern is to query a dedicated L2 sequencer uptime feed and revert with `SequencerDown()` or `GracePeriodNotOver()` before consuming any price data.

### Impact Explanation
The pool contracts use `getRate()` to determine how much rsETH a depositor receives for their collateral. If the stale price is higher than the true market price (e.g., the collateral token dropped in value while the sequencer was down), an attacker can deposit collateral at the inflated stale rate and receive more rsETH than the collateral is worth. This constitutes direct theft of funds from the pool at the expense of other depositors and the protocol.

**Impact: Critical** — direct theft of user funds from the pool.

### Likelihood Explanation
Arbitrum sequencer outages have occurred historically. On Arbitrum, users can bypass the sequencer entirely by force-including transactions through the L1 delayed inbox (`IInbox.createRetryableTicket`), which is a documented and permissionless mechanism. An attacker monitoring the sequencer status can detect downtime, observe the price divergence, and force-include a deposit transaction before the sequencer recovers and the oracle is updated. No privileged access is required.

**Likelihood: Medium** — requires sequencer downtime (a real, recurring event) and knowledge of force-inclusion, but no admin compromise.

### Recommendation
Integrate the Chainlink L2 sequencer uptime feed into `getRate()`. Following Chainlink's documented pattern:

```solidity
(, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
if (answer == 1) revert SequencerDown();
if (block.timestamp - startedAt < GRACE_PERIOD) revert GracePeriodNotOver();
```

Add a `sequencerUptimeFeed` immutable address to `ChainlinkOracleForRSETHPoolCollateral` and perform this check at the top of `getRate()` before calling `latestRoundData()` on the price feed. Also add a heartbeat staleness check (`block.timestamp - timestamp > HEARTBEAT`) to guard against stale prices independently of sequencer status.

### Proof of Concept
1. The L2 sequencer (e.g., Arbitrum) goes offline. The collateral token (e.g., wstETH) drops 15% in market value while the sequencer is down.
2. The Chainlink wstETH/ETH feed on Arbitrum cannot be updated — it still reports the pre-downtime price.
3. Attacker calls `IInbox.createRetryableTicket` on Ethereum L1 to force-include a deposit transaction into `RSETHPool` (or `RSETHPoolNoWrapper`) on Arbitrum.
4. The pool calls `IOracle(supportedTokenOracle[wstETH]).getRate()` → `ChainlinkOracleForRSETHPoolCollateral.getRate()`.
5. `latestRoundData()` returns the stale pre-downtime price. `answeredInRound == roundID` (no new round was pushed), so `StalePrice` is not triggered. `timestamp != 0` and `ethPrice > 0`, so all guards pass.
6. The pool mints rsETH based on the inflated stale price. The attacker receives ~15% more rsETH than the deposited collateral is worth, extracting value from the pool. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol (L26-37)
```text
    function getRate() public view returns (uint256) {
        (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
            AggregatorV3Interface(oracle).latestRoundData();

        if (answeredInRound < roundID) revert StalePrice();
        if (timestamp == 0) revert IncompleteRound();
        if (ethPrice <= 0) revert InvalidPrice();

        uint256 normalizedPrice = uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());

        return normalizedPrice;
    }
```

**File:** contracts/pools/RSETHPool.sol (L27-60)
```text
    function getRate() external view returns (uint256);
}

/// @title RSETHPool
/// @notice This contract is the pool contract for the rsETH pool on *Arbitrum*
/// @dev it differs from other RSETHPool contracts in other chains as it uses LZ_RSETH as the canonical rsETH token of
/// the chain.
/// @dev it was the first RSETHPool contract to be deployed in an L2 hence the legacy variables
contract RSETHPool is ERC20Upgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;

    /// @custom:oz-renamed-from rsETH
    IERC20Upgradeable public wrsETH;
    /// @custom:oz-renamed-from wstETH
    IERC20Upgradeable public legacyWstETH; // legacy variable

    uint256 public feeBps; // Basis points for fees for ETH deposits
    uint256 public feeEarnedInETH;
    /// @custom:oz-renamed-from feeEarnedInWstETH
    uint256 public legacyFeeEarnedInWstETH; // legacy variable

    address public rsETHOracle;
    /// @custom:oz-renamed-from wstETH_ETHOracle
    address public legacyWstETH_ETHOracle; // legacy variable
    /// @custom:oz-renamed-from MANAGER_ROLE
    bytes32 public constant LEGACY_MANAGER_ROLE = keccak256("MANAGER_ROLE");

    // new variables
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");
    bool public isEthDepositEnabled;
    mapping(address token => uint256 feeEarned) public feeEarnedInToken;
    mapping(address token => address oracle) public supportedTokenOracle;
    address[] public supportedTokenList;
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L27-56)
```text
/// @title RSETHPoolNoWrapper
/// @notice This contract is the deposit pool for the chains where there is no rsETH wrapper contract (e.g. Arbitrum,
/// Unichain)
contract RSETHPoolNoWrapper is AccessControlUpgradeable, PausableUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;

    /// @notice Roles
    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    /// @notice The canonical rsETH token address (rsETH OFT)
    IERC20 public rsETH;

    /// @notice Basis points for fees
    uint256 public feeBps;

    /// @notice Fee earned in ETH
    uint256 public feeEarnedInETH;

    /// @notice The rsETHOracle address
    address public rsETHOracle;

    /// @notice Flag to enable/disable native ETH deposits
    bool public isEthDepositEnabled;

    /// @notice Mapping to track fees earned in different tokens
    mapping(address token => uint256 feeEarned) public feeEarnedInToken;

    /// @notice Mapping of supported tokens to their oracles
    mapping(address token => address oracle) public supportedTokenOracle;
```
