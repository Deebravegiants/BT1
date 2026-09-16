### Title
Missing L2 Sequencer Uptime Check in `SimplexPaymaster` Chainlink Price Oracle Usage - (File: `evm/src/utils/SimplezPaymaster.sol`)

### Summary
`SimplexPaymaster` prices ERC‑4337 gas payments using two Chainlink `AggregatorV3Interface` feeds (`nativeOracle` and each token's `tokenOracle`) through `_getOraclePrice`, but never checks whether the L2 sequencer is up before trusting `latestRoundData()`. On sequencer-based L2s where this paymaster is deployed (Optimism, Arbitrum, Base — see the configured feed addresses), a sequencer outage/restart can make `_getOraclePrice` return a price that passes the staleness check (`block.timestamp - updatedAt <= maxOracleAge`) yet does not reflect the real, current market price, exactly the bug class described in the external report about `BondChainlinkOracle` lacking an L2 sequencer uptime check. [1](#0-0) 

### Finding Description
`_getOraclePrice` only validates `answer > 0` and staleness against `maxOracleAge`; it performs no sequencer-uptime check whatsoever: [2](#0-1) 

This price is consumed by `_tokenPrice`, which computes the token amount an ERC-4337 `UserOperation` sender must pay to cover native gas costs: [3](#0-2) 

`_tokenPrice` is invoked from `_fetchDetails`, which runs during **every** UserOp's paymaster validation — a path directly reachable by any unprivileged account (including an intent solver or bandwidth purchaser) that submits a UserOp naming a registered token, with no permission gate: [4](#0-3) 

The same unguarded `_getOraclePrice` call also determines the minimum swap output in `swapAndDeposit` (treasury-only, but still relies on the same unsound price): [5](#0-4) 

The paymaster is deployed on rollups that have a sequencer (Optimism, Arbitrum, Base), as evidenced by the configured Chainlink feed addresses per chain and the deployment scripts: [6](#0-5) [7](#0-6) 

On these networks, Chainlink recommends checking a dedicated sequencer-uptime feed before trusting `latestRoundData()`, because during/after a sequencer outage price feeds can report an `updatedAt` that satisfies the staleness bound while the underlying answer no longer matches the real market price at the moment L2 transactions resume execution. `SimplexPaymaster` has no such check anywhere in its oracle-consuming logic.

### Impact Explanation
Any unprivileged account (including an intent solver using `SolverAccount` as shown in the probe script) can submit UserOps through this paymaster while an L2 sequencer is degraded. If the stale-but-"fresh-enough" oracle answer under-states the native asset's price (or over-states the token's price), the sender pays less ERC-20 token than the true cost of the sponsored gas, directly draining the paymaster's `EntryPoint` deposit and accrued token balance — concrete theft of protocol funds — with no way for governance to intervene in time since these are automatic, permissionless validations on every UserOp. The reverse skew can also overcharge legitimate senders, a fund-freezing/loss condition for users. This mirrors the acknowledged severity of the original `BondChainlinkOracle` finding (Medium, BVSS 5.5).

### Likelihood Explanation
L2 sequencer outages are a recurring, observed real-world event on Optimism/Arbitrum/Base, and exploiting the resulting mispriced window requires no special privilege — merely submitting an ERC-4337 UserOp against an already-registered token, which is the paymaster's normal, permissionless operating mode. No governance or admin action is required to trigger the condition.

### Recommendation
Add a Chainlink L2 sequencer-uptime feed check (mirroring the fix applied to `BondChainlinkOracleL2`) inside `_getOraclePrice` (and thus effective in `_tokenPrice`, `_fetchDetails`, and `swapAndDeposit`): revert if the sequencer feed reports "down," and enforce a grace period after it comes back up before trusting `latestRoundData()` again.

### Proof of Concept
1. Deploy/observe `SimplexPaymaster` on an L2 with a sequencer (e.g., Optimism/Arbitrum), configured per `evm/script/DeploySimplexPaymaster.s.sol`.
2. Sequencer goes down or restarts after downtime; the registered token/USD or native/USD Chainlink feed's `latestRoundData().updatedAt` is still within `maxOracleAge` but the `answer` no longer matches the real-time market price (a known Chainlink L2 sequencer-outage artifact).
3. An unprivileged account submits a UserOp through this paymaster in mode `0x00`/`0x02`, referencing the mispriced token; `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` computes `tokenPrice` from the stale-but-accepted feed data.
4. `PaymasterERC20`'s prefund logic charges the sender based on this mispriced `tokenPrice`, resulting in the sender paying less token than the true gas cost — draining the paymaster's EntryPoint deposit/treasury balance over repeated UserOps during the outage window.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L464-467)
```text
        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;
```

**File:** evm/src/utils/SimplexPaymaster.sol (L524-547)
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

**File:** sdk/packages/indexer/src/addresses/chainlink-price-feeds.addresses.ts (L10-14)
```typescript
	"EVM-1": "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419", // Ethereum Mainnet
	"EVM-8453": "0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70", // Base Mainnet
	"EVM-10": "0x13e3Ee699D1909E989722E753853AE30b17e08c5", // Optimism Mainnet
	"EVM-42161": "0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612", // Arbitrum Mainnet
	"EVM-56": "0x0567F2323251f0Aab15c8dFb1967E4e8A7D42aeE", // BSC Mainnet
```

**File:** evm/script/SimplexPaymasterPermit2Probe.s.sol (L30-34)
```text
contract SimplexPaymasterPermit2ProbeScript is Script {
    address constant HOST = 0x9AA003594d59C62EE17A73A569Fd7B1DbdBd71E1;
    address constant INTENT_GATEWAY_V2 = 0x6CF42FA9BecbC5b6a26884964956b113530f7cFA;
    address constant ETH_USD = 0x4aDC67696bA383F43DD60A9e78F2C97Fbbfc7cb1;
    address constant USDC_USD = 0xd30e2101a97dcbAeBCBC04F14C3f624E67A35165;
```
