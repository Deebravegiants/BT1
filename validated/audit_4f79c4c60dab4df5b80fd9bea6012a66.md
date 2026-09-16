### Title
`SimplexPaymaster._getOraclePrice()` accepts a Chainlink `minAnswer`/`maxAnswer`-clamped price, letting a UserOperation underpay gas during a stablecoin depeg — ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster._getOraclePrice()` validates a Chainlink `latestRoundData()` result only against `answer <= 0` and staleness, never against the aggregator's own min/max circuit-breaker bounds. This is the exact bug class from the referenced report: if the underlying asset price crashes past the feed's configured floor (or spikes past its ceiling), Chainlink keeps returning the clamped `minAnswer`/`maxAnswer` instead of the true price, and the consuming contract silently treats that stale extreme as current market truth. [1](#0-0) 

### Finding Description
`_tokenPrice()` computes the ERC-20 gas price by dividing the native/USD price by the token/USD price, both fetched from `_getOraclePrice()`: [2](#0-1) 

`_getOraclePrice()` itself:

```solidity
function _getOraclePrice(AggregatorV3Interface oracle, uint8 oracleDecimals) internal view returns (uint256) {
    (, int256 answer,, uint256 updatedAt,) = oracle.latestRoundData();
    if (answer <= 0) revert InvalidOraclePrice(address(oracle), answer);
    if (block.timestamp - updatedAt > maxOracleAge) {
        revert StaleOraclePrice(address(oracle), updatedAt);
    }
    ...
}
``` [3](#0-2) 

There is no check that `answer` lies strictly between the aggregator's configured `minAnswer` and `maxAnswer`. Chainlink aggregators have a hard-coded price band; when the true market price moves outside it (e.g. a stablecoin depeg or a violent crash of the native asset), the feed keeps emitting the clamped bound with a fresh `updatedAt`, so neither the `answer <= 0` check nor the staleness check catches it. The paymaster is designed to accept "any token with a Chainlink feed" including USDC/USDT, and is registered with native-asset feeds (ETH/USD, BNB/USD) as documented in the deployment script and tests. [4](#0-3) 

### Impact Explanation
`_getOraclePrice()` feeds directly into `tokenPrice`, which `_prefund` uses to size the exact amount of ERC-20 tokens pulled from a UserOperation sender (via `transferFrom` or `Permit2.permitTransferFrom`) to cover the native gas the paymaster fronts: [5](#0-4) 

Any unprivileged account submitting an ERC-4337 UserOperation through this paymaster — including intent solvers using it to self-fund delegation or bid submission, per the documented flow — controls when their op lands and can choose to submit it while a registered token's feed (e.g. a stablecoin under depeg stress) is clamped at `minAnswer` above the true price. This makes `tokenUsd` look higher than reality, understating `tokenPrice`, so the sender pays fewer tokens than the native gas actually cost the paymaster. Symmetrically, if the native-asset feed is clamped at `minAnswer` during a crash, `nativeUsd` is inflated and senders are overcharged. In the first case this is a direct, repeatable drain of the paymaster's EntryPoint deposit (native funds) — concrete theft of protocol funds — for as long as the underlying feed remains clamped.

### Likelihood Explanation
Requires a real-world price-band breach on a configured feed (native-asset or stablecoin) — historically demonstrated events (e.g. LUNA, USDC/USDT depeg episodes) show this is not merely theoretical for exactly the asset classes this paymaster is documented to support (USDC, USDT, and native ETH/BNB/MATIC feeds). Exploitation requires no privileged access: any address able to submit a UserOperation through the paymaster (an "unprivileged message dispatcher" in ERC-4337 terms) can time transactions to profit while the condition holds, and can repeat it across many ops until governance intervenes via `UpdateParams`/`DeactivateToken`.

### Recommendation
In `_getOraclePrice()`, fetch `minAnswer`/`maxAnswer` from the aggregator (or configure them per feed in `TokenConfig`/`Params`) and revert (e.g. a new `OraclePriceOutOfBounds` error) when `answer` is within a small margin of either bound, in addition to the existing `answer <= 0` and staleness checks.

### Proof of Concept
1. Governance registers a stablecoin (e.g. USDC) with its Chainlink USD feed via `RegisterToken`, as in `_registerToken`. [6](#0-5) 
2. The stablecoin depegs sharply downward in the real market; its Chainlink aggregator's price band floor is hit, so `latestRoundData()` keeps returning `minAnswer` (e.g. $0.98) with a continuously refreshed `updatedAt`, even though the true price is $0.50.
3. An attacker (any UserOperation sender) submits a mode-`0x02` (Permit2) op through `SimplexPaymaster`. `_fetchDetails` → `_tokenPrice` → `_getOraclePrice` computes `tokenUsd = 0.98` (clamped) instead of the true `0.50`, so `tokenPrice` — and thus the tokens pulled in `_prefund` — is roughly half of what should be charged for the same native gas cost. [7](#0-6) 
4. The attacker repeats this across many UserOperations, systematically underpaying for gas and draining the paymaster's EntryPoint deposit (native funds) relative to the stablecoin it collects, until governance detects and reacts via `UpdateParams`/`DeactivateToken`.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L387-404)
```text
    function _registerToken(address token, AggregatorV3Interface oracle) internal {
        if (token == address(0) || address(oracle) == address(0)) revert ZeroAddress();

        bool isNew = !tokenConfigs[token].active && address(tokenConfigs[token].tokenOracle) == address(0);

        tokenConfigs[token] = TokenConfig({
            tokenOracle: oracle,
            tokenOracleDecimals: oracle.decimals(),
            tokenDecimals: IERC20Metadata(token).decimals(),
            active: true
        });

        if (isNew) {
            registeredTokens.push(token);
        }

        emit TokenRegistered(token, address(oracle));
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L516-524)
```text
    /// @dev Returns the token to charge and its price relative to native gas.
    ///
    ///      PaymasterERC20 computes `erc20Cost = weiCost * tokenPrice / 1e18`,
    ///      so tokenPrice must be token base units per wei, scaled by 1e18:
    ///        tokenPrice = (nativeUsd * 10^tokenDecimals) / tokenUsd
    ///      e.g. BNB at $600, USDC at $1 with 6 decimals: 0.001 BNB (1e15 wei)
    ///      should cost 0.60 USDC (600000 units), giving tokenPrice = 6e8, which
    ///      is exactly (600e8 * 1e6) / 1e8. Markup is applied on top.
    function _fetchDetails(
```

**File:** evm/src/utils/SimplexPaymaster.sol (L563-576)
```text
    function _prefund(
        PackedUserOperation calldata userOp,
        bytes32 userOpHash,
        IERC20 token,
        uint256 tokenPrice,
        address prefunder_,
        uint256 maxCost
    )
        internal
        override
        returns (bool prefunded, uint256 prefundAmount, address prefunder, bytes memory prefundContext)
    {
        bytes calldata data = userOp.paymasterData();
        if (uint8(data[0]) != 0x02) {
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

**File:** evm/script/DeploySimplexPaymaster.s.sol (L14-34)
```text
    function deploy() internal override {
        address nativeOracleAddr = config.get("NATIVE_ORACLE").toAddress();
        uint256 markupBps = vm.envOr("MARKUP_BPS", uint256(200)); // default 2%
        address treasury = vm.envOr("TREASURY", admin); // default to deployer
        // Stablecoin feeds on Ethereum and Base run a 24h heartbeat; a buffer over
        // 24h avoids transient StaleOraclePrice reverts on late pushes.
        uint256 maxOracleAge = vm.envOr("MAX_ORACLE_AGE", uint256(90_000));
        uint256 swapSlippageBps = vm.envOr("SWAP_SLIPPAGE_BPS", uint256(200)); // default 2%
        address relayer = vm.envAddress("GOVERNANCE_RELAYER");
        require(relayer != address(0), "GOVERNANCE_RELAYER is unset");

        bool hasUsdt = config.exists("USDT_TOKEN") && config.exists("USDT_ORACLE");
        uint256 tokenCount = hasUsdt ? 2 : 1;
        address[] memory tokens = new address[](tokenCount);
        AggregatorV3Interface[] memory oracles = new AggregatorV3Interface[](tokenCount);
        tokens[0] = config.get("USDC_TOKEN").toAddress();
        oracles[0] = AggregatorV3Interface(config.get("USDC_ORACLE").toAddress());
        if (hasUsdt) {
            tokens[1] = config.get("USDT_TOKEN").toAddress();
            oracles[1] = AggregatorV3Interface(config.get("USDT_ORACLE").toAddress());
        }
```
