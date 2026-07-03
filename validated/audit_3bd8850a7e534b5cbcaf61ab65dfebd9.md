Audit Report

## Title
Missing L2 Sequencer Uptime Check Enables Stale-Price Exploitation on Arbitrum - (File: `contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol`)

## Summary
`ChainlinkOracleForRSETHPoolCollateral.getRate()` calls Chainlink's `latestRoundData()` on Arbitrum without verifying the L2 sequencer is live. During a sequencer outage, Chainlink L2 feeds freeze at their last-known values; the existing `answeredInRound < roundID` guard never triggers because no new round is opened, so the stale price is returned silently. Any unprivileged depositor can call `RSETHPool.deposit(token, amount, referralId)` at the frozen (pre-outage) price and receive more rsETH than the deposited collateral is worth at current market value, extracting value from the pool and diluting existing rsETH holders.

## Finding Description
`ChainlinkOracleForRSETHPoolCollateral.getRate()` fetches the collateral-to-ETH rate with no sequencer liveness check:

```solidity
// contracts/pools/oracle/ChainlinkOracleForRSETHPoolCollateral.sol L26-37
function getRate() public view returns (uint256) {
    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();   // ← does NOT fire during sequencer downtime
    if (timestamp == 0) revert IncompleteRound();
    if (ethPrice <= 0) revert InvalidPrice();
    ...
}
``` [1](#0-0) 

When the Arbitrum sequencer is down, Chainlink stops publishing new rounds. The last round remains open with `answeredInRound == roundID`, so `StalePrice` never reverts. The `timestamp == 0` guard only catches an uninitialized round, not a frozen one.

This oracle is consumed directly by `RSETHPool.viewSwapRsETHAmountAndFee`:

```solidity
// contracts/pools/RSETHPool.sol L343-346
uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();
rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
``` [2](#0-1) 

which is called by the public `deposit(address token, uint256 amount, string referralId)` function: [3](#0-2) 

Full call chain: `deposit(token, amount, referralId)` → `viewSwapRsETHAmountAndFee(amount, token)` → `IOracle(supportedTokenOracle[token]).getRate()` → `ChainlinkOracleForRSETHPoolCollateral.getRate()` → returns frozen price.

If the collateral token (e.g., wstETH) drops in price during the outage while the rsETH oracle reflects a different (or also frozen but divergent) rate, `rsETHAmount` is inflated. The attacker receives wrsETH backed by less collateral than the issued amount represents.

## Impact Explanation
**High — Theft of unclaimed yield.**

The attacker deposits collateral at a stale, inflated `tokenToETHRate` and receives more wrsETH than the collateral is worth at current market prices. The pool issues wrsETH against under-valued collateral, permanently diluting the rsETH/ETH backing ratio. Existing rsETH holders bear the loss through reduced backing per token — this constitutes theft of unclaimed yield from the protocol and its depositors. The attack requires no special permissions and is repeatable for the full duration of any sequencer outage.

## Likelihood Explanation
The Arbitrum sequencer has experienced documented outages. The contract is explicitly annotated as the Arbitrum pool: [4](#0-3) 

No privileges are required — any external address can call `deposit(token, amount, referralId)`. The `whenNotPaused` modifier provides a partial mitigation only if the protocol's PAUSER_ROLE holder manually pauses the contract during the outage window, which is not guaranteed and introduces operational dependency. The attack window is open for the entire duration of any sequencer downtime.

## Recommendation
Add a Chainlink L2 Sequencer Uptime Feed check at the top of `getRate()` in `ChainlinkOracleForRSETHPoolCollateral.sol`:

```solidity
AggregatorV3Interface public immutable sequencerUptimeFeed;
uint256 public constant GRACE_PERIOD = 3600; // 1 hour after sequencer restart

function getRate() public view returns (uint256) {
    (, int256 sequencerAnswer, uint256 startedAt,,) = sequencerUptimeFeed.latestRoundData();
    // sequencerAnswer == 1 means sequencer is down; enforce grace period after restart
    if (sequencerAnswer == 1 || block.timestamp - startedAt < GRACE_PERIOD) {
        revert SequencerDown();
    }

    (uint80 roundID, int256 ethPrice,, uint256 timestamp, uint80 answeredInRound) =
        AggregatorV3Interface(oracle).latestRoundData();

    if (answeredInRound < roundID) revert StalePrice();
    if (timestamp == 0) revert IncompleteRound();
    if (ethPrice <= 0) revert InvalidPrice();

    return uint256(ethPrice) * 1e18 / 10 ** uint256(AggregatorV3Interface(oracle).decimals());
}
```

The Arbitrum sequencer uptime feed address is `0xFdB631F5EE196F0ed6FAa767959853A9F217697D`. The same pattern should be applied to any other Chainlink-based oracle deployed on L2.

## Proof of Concept

1. Fork Arbitrum mainnet at a block just before a known sequencer outage (or simulate by mocking `latestRoundData` to return a frozen round).
2. Deploy/connect to `RSETHPool` and `ChainlinkOracleForRSETHPoolCollateral` with wstETH as a supported collateral.
3. Advance time by the outage duration; mock the wstETH/ETH Chainlink feed to return the pre-outage price (e.g., 1.2e18) while the true market price has dropped to 1.0e18.
4. Call `RSETHPool.deposit(wstETH, 100e18, "")` as an unprivileged attacker.
5. Assert that `viewSwapRsETHAmountAndFee` returns `rsETHAmount` calculated at 1.2e18 rather than 1.0e18 — the attacker receives ~20% more wrsETH than the deposited wstETH is worth.
6. Confirm `answeredInRound == roundID` throughout, proving `StalePrice` never reverts.

Foundry fork test skeleton:
```solidity
function testSequencerDownStalePrice() public {
    // mock latestRoundData: answeredInRound == roundID, price = pre-outage value
    vm.mockCall(chainlinkFeed, abi.encodeWithSelector(AggregatorV3Interface.latestRoundData.selector),
        abi.encode(uint80(10), int256(1.2e8), uint256(0), block.timestamp - 7200, uint80(10)));

    uint256 rsETHOut = rsETHPool.viewSwapRsETHAmountAndFee(100e18, wstETH);
    // rsETHOut should be inflated vs. fair value at 1.0e8 price
    assertGt(rsETHOut, fairValueRsETHOut);
}
```

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

**File:** contracts/pools/RSETHPool.sol (L30-35)
```text
/// @title RSETHPool
/// @notice This contract is the pool contract for the rsETH pool on *Arbitrum*
/// @dev it differs from other RSETHPool contracts in other chains as it uses LZ_RSETH as the canonical rsETH token of
/// the chain.
/// @dev it was the first RSETHPool contract to be deployed in an L2 hence the legacy variables
contract RSETHPool is ERC20Upgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
```

**File:** contracts/pools/RSETHPool.sol (L284-305)
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
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        IERC20(address(wrsETH)).safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId); // Add token address?
    }
```

**File:** contracts/pools/RSETHPool.sol (L343-346)
```text
        uint256 tokenToETHRate = IOracle(supportedTokenOracle[token]).getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * tokenToETHRate / rsETHToETHrate;
```
