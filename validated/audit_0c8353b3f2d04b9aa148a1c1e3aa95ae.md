Confirmed: `SimplexPaymaster` is deployed on Arbitrum mainnet (`0x7281Bccb4f0BCE44F3B8542d1fC5e51c2F5fC08C`) [1](#0-0) , and its `_getOraclePrice` function only checks answer positivity and staleness against `maxOracleAge`, never a Chainlink L2 sequencer-uptime feed [2](#0-1) .

### Title
`SimplexPaymaster` prices ERC-20 gas payments using Chainlink feeds without an Arbitrum L2 sequencer-uptime check, allowing fee mispricing during sequencer downtime/recovery - (File: `evm/src/utils/SimplexPaymaster.sol`)

### Summary
`SimplexPaymaster` is an ERC-4337 paymaster deployed on Arbitrum (and other chains) that lets any user pay UserOperation gas in whitelisted ERC-20 tokens, priced via Chainlink `latestRoundData()` feeds for `native/USD` and `token/USD` [3](#0-2) . The `_getOraclePrice` helper only reverts on a non-positive answer or on `block.timestamp - updatedAt > maxOracleAge`; it never queries the Chainlink `SequencerUptimeFeed` recommended for Arbitrum integrations [4](#0-3) .

### Finding Description
On Arbitrum, when the sequencer is offline and later resumes, Chainlink price feeds can report a technically "fresh" `updatedAt` timestamp (once the sequencer batches catch up) while the underlying price is stale relative to the true off-chain market, or conversely a genuinely fresh update may arrive well after the true market price has moved. Chainlink explicitly documents this risk and recommends gating any L2 price consumption on a `SequencerUptimeFeed` with a grace period (https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code). `_getOraclePrice` in `SimplexPaymaster.sol` performs none of these checks — it is a plain `latestRoundData()` read gated only by staleness/positivity [2](#0-1) . This value directly feeds `_tokenPrice`, which is used both to determine `tokenPrice` for prefunding a UserOperation (`_fetchDetails`) and for the actual token pull in `_prefund`/`_executePermit` flows [5](#0-4) . Any unprivileged account (a "bandwidth purchaser" paying for its own transaction's gas in an ERC-20 via this paymaster) can submit a UserOperation at any block during or immediately after an Arbitrum sequencer outage and have its gas cost computed from oracle data that Chainlink's own guidance says must not be trusted without a sequencer-uptime gate.

### Impact Explanation
During/after sequencer downtime, a user can time UserOperations so that `nativeUsd`/`tokenUsd` reflects a stale-but-passing-staleness-check price, letting them pay a systematically mispriced (too-low) amount of the ERC-20 fee token relative to the true gas cost in native currency, or vice versa. Since `SimplexPaymaster` is the sole entity fronting gas for these ops and immediately recycling collected fees to native/treasury (`FeesRecycled`) [6](#0-5) , this results in the treasury/paymaster absorbing an under-collected gas cost, i.e. a value leak per exploited op — a concrete loss of protocol funds. This is a medium-severity funds-drain vector reachable by any single transaction from an unprivileged account, matching the referenced bug class.

### Likelihood Explanation
Exploitability requires a real Arbitrum sequencer outage/recovery window — an infrequent but historically recurring event on Arbitrum — combined with an attacker (or opportunistic user) monitoring sequencer status and timing gas-payment UserOperations through this specific paymaster. Because `maxOracleAge` is governance-configurable and can be set loosely, and there is no sequencer-liveness gate at all, exploitation only needs the outage window plus a normal `PERMIT`/`PERMIT2` paymasterData submission — no privileged access required.

### Recommendation
Add the Chainlink `SequencerUptimeFeed` check recommended in https://docs.chain.link/data-feeds/l2-sequencer-feeds#example-code to `_getOraclePrice` (or `_tokenPrice`): verify the sequencer is up (`answer == 0`) and that at least a grace period (e.g. 1 hour) has elapsed since it came back up before trusting `latestRoundData()` results on Arbitrum deployments; revert (or fall back to a safe default/pause) otherwise.

### Proof of Concept
1. Arbitrum sequencer goes offline for an extended period; Chainlink feeds stop receiving new rounds but `updatedAt` was recent enough to remain within `maxOracleAge` once the sequencer resumes and `block.timestamp` catches up.
2. During the resumption window, off-chain market price of the ERC-20 fee token or native asset has moved materially from the last on-chain round, but `_getOraclePrice` in `evm/src/utils/SimplexPaymaster.sol` (lines 662-676) still returns that stale round's `answer` because it is within `maxOracleAge` and positive.
3. An attacker submits a `PackedUserOperation` with `paymasterData` mode `0x00`/`0x02` referencing the mispriced token; `_fetchDetails` computes `tokenPrice` from the stale oracle read (lines 516-546), and `_prefund`/`PaymasterERC20._postOp` settle the ERC-20 transfer at that mispriced rate.
4. The paymaster/treasury receives less value than the true gas cost, repeatable for every UserOperation submitted during the exposure window, draining SimplexPaymaster's treasury funds.

### Citations

**File:** docs/content/developers/evm/contract-addresses/mainnet.mdx (L47-51)
```text
| `SimplexPaymaster` | [`0x7281Bccb4f0BCE44F3B8542d1fC5e51c2F5fC08C`](https://arbiscan.io/address/0x7281Bccb4f0BCE44F3B8542d1fC5e51c2F5fC08C) |
| `SimplexPaymaster (Implementation)` | [`0x58F678b5dA7997C7121621495ECFD8984D525e79`](https://arbiscan.io/address/0x58F678b5dA7997C7121621495ECFD8984D525e79) |
| `BandwidthManager` | [`0x6A67533Ce73756FfaB17c05578A5FBBa5d9B2d8d`](https://arbiscan.io/address/0x6A67533Ce73756FfaB17c05578A5FBBa5d9B2d8d) |
| `ConsensusStateId` | Messaging: `ETH0` / Consensus: `ARB0` |
| `StateMachine` | `EVM-42161` |
```

**File:** evm/src/utils/SimplexPaymaster.sol (L223-223)
```text
    event FeesRecycled(address indexed token, uint256 amountIn, uint256 nativeOut, uint256 deposited);
```

**File:** evm/src/utils/SimplexPaymaster.sol (L516-546)
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
