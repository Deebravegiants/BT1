### Title
Missing Arbitrum Sequencer Uptime Check in `SimplexPaymaster._getOraclePrice` Allows Stale/Mispriced Gas-Fee Charges - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is an ERC-4337 paymaster deployed across multiple chains — including Arbitrum Mainnet, per the Chainlink feed registry — that lets any unprivileged UserOperation sender pay gas in a registered ERC-20 by converting native gas cost to token cost through two Chainlink `AggregatorV3Interface` feeds. `_getOraclePrice()` only validates that the Chainlink answer is positive and that `block.timestamp - updatedAt <= maxOracleAge`; it never checks the Arbitrum L2 Sequencer Uptime feed. When the Arbitrum sequencer is down, Chainlink price updates freeze but remain within the staleness window, so the paymaster keeps computing gas costs from a price that no longer reflects the real market — enabling under- or over-charging of every gas-paying UserOperation processed during (and immediately after) a sequencer outage.

### Finding Description
`_getOraclePrice` in `evm/src/utils/SimplexPaymaster.sol` is:
```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();
    if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
    if (block.timestamp - updatedAt > maxOracleAge) {
        revert StaleOraclePrice(address(oracle), updatedAt);
    }
    ...
}
``` [1](#0-0) 

This is used by `_tokenPrice()`, which is called from both the permissionless validation-time pricing path `_fetchDetails()` (called by `PaymasterERC20.validatePaymasterUserOp`, itself invoked by the ERC-4337 `EntryPoint` for any submitted UserOperation) and from `swapAndDeposit()`: [2](#0-1) [3](#0-2) 

The `maxOracleAge` staleness bound only guards against the *feed's own reporter* going silent for too long; it does nothing about the *chain* (Arbitrum) being unable to relay fresh price data because its sequencer is offline. On Arbitrum, Chainlink price updates are transactions submitted through the sequencer; when the sequencer halts, `updatedAt` simply stops advancing while remaining "fresh enough" relative to `maxOracleAge` (governance-configurable up to `MAX_ORACLE_AGE = 7 days`, and the code comments note some feeds heartbeat "up to 24h"). During that window, the true off-chain USD price of the native asset or the ERC-20 token may have moved substantially (e.g. de-peg, crash), but the paymaster keeps using the last on-chain price as if it were current, exactly the class of bug flagged by Chainlink's L2 sequencer-uptime-feed guidance.

Any bandwidth purchaser (the sender of an ERC-4337 UserOperation) can trigger the affected code path with zero special privilege — `_fetchDetails`/`_tokenPrice`/`_getOraclePrice` execute unconditionally as part of standard fee accounting for every gas-sponsored operation.

### Impact Explanation
Because the token/native conversion price feeds this discrepancy directly into the amount of ERC-20 pulled from the UserOperation sender in `_prefund` (both the permit path via `super._prefund`/`_erc20Cost` and the Permit2 path via `PERMIT2.permitTransferFrom` with `prefundAmount = _erc20Cost(...)`), a stale price during an Arbitrum sequencer outage:
- Lets senders systematically under-pay for gas relative to real market value, draining the paymaster's native EntryPoint deposit/treasury surplus over time (a concrete loss of protocol funds), or
- Forces senders to overpay, siphoning value from users into the treasury without their consent.

This is a direct, exploitable fund-flow distortion reachable by any unprivileged UserOperation sender, not merely a display or monitoring issue, and it persists for as long as the sequencer outage plus the configured `maxOracleAge` window.

### Likelihood Explanation
Arbitrum sequencer outages are a documented, recurring occurrence (Chainlink explicitly recommends sequencer-uptime checks for this reason), and `SimplexPaymaster` is intended to run on Arbitrum (its price-feed address registry includes `EVM-42161`/Arbitrum Mainnet and `EVM-421614`/Arbitrum Sepolia). Any actor who can submit or observe a bundler-processed UserOperation during such an outage can exploit the mispricing without needing privileged access, elevated gas, or race conditions beyond simply timing submission to the outage window.

### Recommendation
Add an Arbitrum L2 Sequencer Uptime Feed check (Chainlink `FlagsInterface`/`AggregatorV2V3Interface`-style sequencer status oracle) to `_getOraclePrice()` (or a wrapper invoked before pricing), and revert (or otherwise refuse to price/charge) whenever the sequencer is reported down, plus enforce a grace period after it comes back up before trusting fresh price data again, consistent with Chainlink's recommended L2 pattern.

### Proof of Concept
1. Deploy/observe `SimplexPaymaster` on Arbitrum with a registered token and `nativeOracle`/`tokenOracle` pointing at Chainlink feeds, `maxOracleAge` set to a multi-hour/day value as allowed by `MAX_ORACLE_AGE = 7 days` (`evm/src/utils/SimplexPaymaster.sol:165`).
2. Arbitrum sequencer halts; on-chain Chainlink feed `updatedAt` stops advancing but stays within `maxOracleAge` of `block.timestamp` once transactions resume flowing through the (recovering) sequencer or via L1 force-inclusion.
3. Meanwhile the true off-chain USD price of the native asset or token has diverged materially (e.g., market crash/de-peg during the outage).
4. A UserOperation with `paymasterData` mode `0x00` or `0x02` is submitted; `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` returns the stale-but-"fresh-enough" price (`evm/src/utils/SimplexPaymaster.sol:662-676`), and `_prefund`/`_erc20Cost` charges the sender based on this incorrect conversion rate (`evm/src/utils/SimplexPaymaster.sol:563-610`), realizing an economic loss for either the treasury or the sender depending on price direction — with no code path checking sequencer liveness to prevent it.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L524-556)
```text
    function _fetchDetails(
        PackedUserOperation calldata userOp,
        bytes32 /* userOpHash */
    )
        internal
        view
        override
        returns (uint256 validationData, IERC20 token, uint256 tokenPrice)
    {
        bytes calldata data = userOp.paymasterData();
        if (data.length < 21) revert InvalidPaymasterData(data.length);

        uint8 mode = uint8(data[0]);
        if (mode != 0x00 && mode != 0x02) revert InvalidMode(mode);

        address tokenAddr = address(bytes20(data[1:21]));

        TokenConfig memory cfg = tokenConfigs[tokenAddr];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(tokenAddr);
        if (!cfg.active) revert TokenNotActive(tokenAddr);

        tokenPrice = _tokenPrice(cfg);
        token = IERC20(tokenAddr);
        validationData = 0; // no time-range restriction

        if (mode == 0x02) {
            (,,, uint256 deadline,,,) = _parsePermit2Data(data);
            // Surfacing the permit deadline as validUntil lets bundlers drop
            // expiring ops instead of discovering it through a Permit2 revert.
            uint48 validUntil = deadline > type(uint48).max ? 0 : uint48(deadline);
            validationData = ERC4337Utils.packValidationData(true, 0, validUntil);
        }
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L653-658)
```text
    function _tokenPrice(TokenConfig memory cfg) internal view returns (uint256) {
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);

        return (nativeUsd * (10 ** cfg.tokenDecimals) * (10_000 + markupBps)) / (tokenUsd * 10_000);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L660-676)
```text
    /// @dev Fetch a Chainlink price normalized to 8 decimals.
    ///      Reverts on stale or non-positive answers.
    function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
        (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();

        if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
        if (block.timestamp - updatedAt > maxOracleAge) {
            revert StaleOraclePrice(address(oracle), updatedAt);
        }

        if (oracleDecimals < 8) {
            return uint256(answer) * (10 ** (8 - oracleDecimals));
        } else if (oracleDecimals > 8) {
            return uint256(answer) / (10 ** (oracleDecimals - 8));
        }
        return uint256(answer);
    }
```
