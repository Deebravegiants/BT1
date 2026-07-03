### Title
Chainlink Oracle on L2 Pools Has No Sequencer Uptime Check, Enabling Stale-Price Exploitation After Sequencer Downtime - (File: contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol)

### Summary
`ChainlinkOracleForRSETHPoolCollateral` is used as the collateral token price oracle in L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV3WithNativeChainBridge`). It calls Chainlink's `latestRoundData()` but performs no check against the Chainlink L2 Sequencer Uptime Feed. When an L2 sequencer goes down and comes back online, the Chainlink price feed on L2 will return the last pre-downtime price, which may be significantly stale. An unprivileged attacker can exploit this window to deposit collateral at the inflated stale price and receive more `wrsETH` than the collateral is actually worth, causing direct loss to the protocol and existing rsETH holders.

### Finding Description

`ChainlinkOracleForRSETHPoolCollateral.getRate()` fetches the collateral token price via `latestRoundData()` and applies three checks:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol
function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (timestamp == 0) revert IncompleteRound();
    if (ethPrice <= 0) revert InvalidPrice();
    ...
}
```

None of these checks detect L2 sequencer downtime. During sequencer downtime, Chainlink's L2 price feeds stop updating. When the sequencer resumes, the latest round data is still the pre-downtime data: `answeredInRound == roundID` (the round was answered before downtime), `timestamp != 0`, and `ethPrice > 0`. All three guards pass, yet the price is arbitrarily stale.

This oracle is consumed by `RSETHPoolV3.deposit(address token, uint256 amount, ...)` and `RSETHPoolV3WithNativeChainBridge.deposit(address token, uint256 amount, ...)` via `viewSwapRsETHAmountAndFee(amount, token)`:

```solidity
// RSETHPoolV3.sol (deposit with token)
function deposit(address token, uint256 amount, string memory referralId)
    external nonReentrant whenNotPaused onlySupportedToken(token) limitDailyMint(amount, token)
{
    IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
}
```

`viewSwapRsETHAmountAndFee` calls `IOracle(supportedTokenOracle[token]).getRate()` to price the deposited token in ETH terms, then divides by the rsETH/ETH rate to compute how many `wrsETH` to mint. If the collateral token's price is stale-high (e.g., the token crashed during sequencer downtime but the oracle still shows the pre-crash price), the attacker receives more `wrsETH` than the deposited collateral is worth.

`RSETHPoolV3WithNativeChainBridge` is explicitly an L2 contract — it holds `l1VaultETHForL2Chain`, uses `IL2TokenBridge`, and bridges assets back to L1. `RSETHPoolV3` similarly operates on L2 chains. Both rely on `ChainlinkOracleForRSETHPoolCollateral` for collateral token pricing.

### Impact Explanation

**Critical — Direct theft of user/protocol funds.**

An attacker deposits collateral tokens at a stale inflated price immediately after the sequencer resumes. They receive `wrsETH` minted at the old (higher) collateral valuation. Since `wrsETH` is redeemable for ETH at the true rsETH/ETH rate, the attacker extracts more ETH value than they deposited. The loss is borne by all existing rsETH holders through dilution of the backing pool. The magnitude scales with: (a) the price drop of the collateral during downtime, (b) the daily mint limit, and (c) how quickly the attacker acts before the oracle is updated.

### Likelihood Explanation

L2 sequencer outages are a documented, recurring event on Arbitrum, Optimism, and other OP-stack chains. The attack window opens the moment the sequencer resumes and closes when Chainlink's L2 feed is updated (typically within minutes to hours). The attacker needs only a standard EOA and knowledge of the sequencer restart — no privileged access, no governance capture. The attack is straightforward to automate by monitoring the sequencer uptime feed and submitting a deposit transaction in the first block after restart.

### Recommendation

Add a Chainlink L2 Sequencer Uptime Feed check inside `ChainlinkOracleForRSETHPoolCollateral.getRate()`, and revert if the sequencer is down or has been back online for less than a grace period (e.g., 1 hour):

```solidity
// Add sequencer feed address as an immutable
AggregatorV3Interface public immutable sequencerUptimeFeed;
uint256 public constant GRACE_PERIOD = 1 hours;

function getRate() public view returns (uint256) {
    // Check sequencer uptime
    (, int256 answer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
    if (answer != 0) revert SequencerDown();
    if (block.timestamp - startedAt < GRACE_PERIOD) revert GracePeriodNotOver();

    // Existing checks
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();
    if (answeredInRound < roundID) revert StalePrice();
    if (timestamp == 0) revert IncompleteRound();
    if (ethPrice <= 0) revert InvalidPrice();
    ...
}
```

Additionally, add a maximum staleness check (e.g., `block.timestamp - timestamp > MAX_STALENESS`) to catch feeds that are stale for reasons other than sequencer downtime.

### Proof of Concept

1. Protocol deploys `RSETHPoolV3WithNativeChainBridge` on Arbitrum with `wstETH` as a supported token, oracle set to `ChainlinkOracleForRSETHPoolCollateral(wstETH/ETH Chainlink feed)`.
2. `wstETH/ETH` Chainlink feed on Arbitrum last updated at price `P_old = 1.15 ETH` before sequencer downtime.
3. During sequencer downtime, `wstETH` market price drops to `P_new = 1.05 ETH` on L1/CEXes.
4. Sequencer restarts. Chainlink L2 feed still returns `P_old = 1.15 ETH` (not yet updated). `answeredInRound == roundID`, `timestamp != 0`, `ethPrice > 0` — all checks pass.
5. Attacker calls `deposit(wstETH, 1000e18, "")`:
   - `getRate()` returns `1.15e18` (stale)
   - `rsETHAmount = 1000e18 * 1.15e18 / rsETHPrice` — attacker receives rsETH valued at 1150 ETH worth of backing
   - Attacker deposited only 1000 wstETH worth 1050 ETH at true market price
6. Attacker redeems/bridges `wrsETH` for ~1150 ETH equivalent, netting ~100 ETH profit at the expense of the protocol's backing pool. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L34-82)
```text
contract RSETHPoolV3WithNativeChainBridge is ERC20Upgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;

    // ===== Storage layout matching RSETHPoolV3 =====
    IERC20WrsETH public wrsETH;
    uint256 public feeBps; // Basis points for fees
    uint256 public feeEarnedInETH;
    address public rsETHOracle;

    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");

    bool public isEthDepositEnabled;
    mapping(address token => uint256 feeEarned) public feeEarnedInToken;
    mapping(address token => address oracle) public supportedTokenOracle;
    address[] public supportedTokenList;

    /// @notice New variable added for pausable functionality
    bool public paused;

    /// @notice ETH identifier address
    address public constant ETH_IDENTIFIER = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;

    /// @notice The daily minting limit for rsETH
    uint256 public dailyMintLimit;

    /// @notice The amount of rsETH that was minted today
    uint256 public dailyMintAmount;

    /// @notice The last day that rsETH was minted
    uint256 public lastMintDay;

    /// @notice The start timestamp for the daily minting limit
    uint256 public startTimestamp;

    /// @notice The pauser role identifier
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @notice The timelock role identifier
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    /// @notice The corresponding L1Vault contract for the L2 chain
    address public l1VaultETHForL2Chain;

    /// @notice The mapping of token addresses to their respective token bridges
    mapping(address token => address bridge) public tokenBridge;

    /// @notice The operator role identifier
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L280-320)
```text
    /// @dev Swaps ETH for rsETH
    /// @param referralId The referral id
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }

    /// @dev Swaps supported token for rsETH
    /// @param token The token address
    /// @param amount The amount of token
    /// @param referralId The referral id
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
```
