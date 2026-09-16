Confirmed: `SimplexPaymaster` is deployed to Arbitrum (mainnet chain id 42161 configured in `evm/foundry.toml`, and `arbitrum`/`arbitrum-sepolia` RPC endpoints wired for deployment via `evm/script/DeploySimplexPaymaster.s.sol`) and prices gas payments in USDC/USDT using raw Chainlink `AggregatorV3Interface.latestRoundData()` calls with only a staleness/positivity check — no L2 sequencer-uptime check.

### Title
Missing Arbitrum L2 sequencer-uptime check in `SimplexPaymaster` oracle pricing lets stale/frozen Chainlink prices be accepted, causing incorrect USDC/USDT gas pricing - ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 paymaster deployed on Arbitrum (and other L2s) that prices USDC/USDT gas payments using Chainlink `AggregatorV3Interface` feeds [1](#0-0) . Its `_getOraclePrice` function only checks that the answer is positive and that `updatedAt` is within `maxOracleAge`, but never verifies that the Arbitrum sequencer is up via Chainlink's `L2SequencerUptimeFeed`, so an Arbitrum sequencer outage can produce accepted-but-stale/incorrect USDC pricing for any unprivileged UserOp submitted through this paymaster.

### Finding Description
`_getOraclePrice` fetches `latestRoundData()` from the configured token and native oracles and reverts only on non-positive answers or staleness beyond `maxOracleAge`: [2](#0-1) 

This price feeds directly into `_tokenPrice`, which is used both for validating a UserOp's prefund (`_fetchDetails`/`_validatePaymasterUserOp` path, reachable by any unprivileged sender submitting an ERC-4337 UserOp through this permissionless paymaster) and for external gas-cost estimation: [3](#0-2) 

Chainlink explicitly recommends that any consumer on an L2 like Arbitrum check the `L2SequencerUptimeFeed` before trusting a price feed's `updatedAt`/`answer`, because when the sequencer is down, L2-submitted price updates stop being processed but the last-known `updatedAt` can still appear "fresh" relative to `block.timestamp` once the sequencer comes back online and catches up on blocks, or during the outage the feed can silently stop updating without the contract knowing the underlying chain is unavailable for verification. `SimplexPaymaster` is deployed to Arbitrum per the RPC/etherscan configuration in `evm/foundry.toml` (`arbitrum = { chain = 42161 ... }`, `arbitrum-sepolia = { chain = 421614 ...}`) and the deployment script wires in per-chain USDC/USDT Chainlink oracle addresses: [4](#0-3) 

No sequencer-uptime feed, interface, or check exists anywhere in the contract (`grep` for "sequencer"/"Arbitrum" across `evm/src` returns no matches inside `SimplexPaymaster.sol`), unlike other places in the repo that carefully model L2 consensus/finality assumptions (e.g., the OP-stack L2 oracle client) [5](#0-4) .

### Impact Explanation
If the Arbitrum sequencer stalls or goes down, the Chainlink price feeds it depends on (USDC/USD, native ETH/USD) can be stale/incorrect while still passing the `maxOracleAge` freshness check the moment the sequencer resumes and posts a burst of blocks, or malicious/anomalous conditions during an outage can be exploited to price gas incorrectly. Since `_tokenPrice` gates how much USDC/USDT is pulled from any unprivileged UserOp sender via `_prefund`/Permit2 flows, an incorrect price can cause the paymaster to under- or over-charge users, potentially draining excess stablecoin value from senders or letting an attacker underpay for gas relative to the true native-asset cost — a fund-safety issue reachable by any sender constructing a UserOp through this permissionless, unprivileged paymaster path.

### Likelihood Explanation
Likelihood is tied to the frequency and severity of Arbitrum sequencer downtime, which is an infrequent but recurring, externally-documented event (not attacker-controlled), and the bug requires no privileged actor — any user submitting a UserOp during/immediately after such an outage window is affected, and the current staleness check alone does not reliably detect it.

### Recommendation
Integrate Chainlink's `L2SequencerUptimeFeed` for Arbitrum in `_getOraclePrice` (or a wrapper around it): read `latestRoundData()` from the sequencer-uptime feed, revert if `answer == 1` (sequencer down) or if the time since the sequencer came back up is less than a configured grace period, before trusting the token/native price feeds, mirroring Chainlink's documented pattern (https://docs.chain.link/data-feeds#l2-sequencer-uptime-feeds).

### Proof of Concept
1. Deploy `SimplexPaymaster` on Arbitrum with a Chainlink USDC/USD and ETH/USD feed as configured by `DeploySimplexPaymaster.s.sol`.
2. Simulate an Arbitrum sequencer outage (per Chainlink's L2 testing pattern: sequencer stops posting L2 batches to L1, so the L2 timestamp — and thus what `updatedAt` on the price feed reads relative to `block.timestamp` — can misrepresent true feed freshness during/after the outage).
3. Submit a UserOp with `paymasterData` referencing USDC through the harness `fetchDetails`/`_validatePaymasterUserOp` (as exercised in `SimplexPaymasterTest.t.sol`'s oracle-safety tests) [6](#0-5) .
4. Observe that `_getOraclePrice` accepts the price with no sequencer-uptime validation, since no such check exists in `SimplexPaymaster.sol`, allowing the UserOp to be priced/prefunded off a price that should have been rejected had the sequencer's status been checked.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L17-25)
```text
/// @notice Minimal Chainlink AggregatorV3 interface — no external dependency needed.
interface AggregatorV3Interface {
    function latestRoundData()
        external
        view
        returns (uint80 roundId, int256 answer, uint256 startedAt, uint256 updatedAt, uint80 answeredInRound);

    function decimals() external view returns (uint8);
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

**File:** evm/src/utils/SimplexPaymaster.sol (L662-676)
```text
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

**File:** evm/script/DeploySimplexPaymaster.s.sol (L31-65)
```text
        if (hasUsdt) {
            tokens[1] = config.get("USDT_TOKEN").toAddress();
            oracles[1] = AggregatorV3Interface(config.get("USDT_ORACLE").toAddress());
        }

        SimplexPaymaster implementation = new SimplexPaymaster{salt: salt}();
        bytes memory initData = abi.encodeCall(
            SimplexPaymaster.initialize,
            (
                HOST_ADDRESS,
                SimplexPaymaster.Params({
                    nativeOracle: AggregatorV3Interface(nativeOracleAddr),
                    markupBps: markupBps,
                    treasury: treasury,
                    maxOracleAge: maxOracleAge,
                    swapSlippageBps: swapSlippageBps
                }),
                tokens,
                oracles,
                relayer
            )
        );
        ERC1967Proxy proxy = new ERC1967Proxy{salt: salt}(address(implementation), initData);
        SimplexPaymaster paymaster = SimplexPaymaster(payable(address(proxy)));

        console.log("SimplexPaymaster implementation deployed at:", address(implementation));
        console.log("SimplexPaymaster proxy deployed at:", address(paymaster));
        console.log("  host:", HOST_ADDRESS);
        console.log("  nativeOracle:", nativeOracleAddr);
        console.log("  markupBps:", markupBps);
        console.log("  maxOracleAge:", maxOracleAge);
        console.log("  treasury:", treasury);
        console.log("  swapSlippageBps:", swapSlippageBps);
        console.log("  relayer:", relayer);
        console.log("  Registered USDC:", tokens[0], "oracle:", address(oracles[0]));
```

**File:** tesseract/consensus/op-host/src/lib.rs (L293-318)
```rust
	pub async fn latest_event(
		&self,
		from: u64,
		to: u64,
	) -> Result<Option<L2OutputOracle::OutputProposed>, anyhow::Error> {
		if from > to {
			return Ok(None);
		}
		let l2_oracle = self
			.l2_oracle
			.ok_or_else(|| anyhow!("L2 Oracle address is missing for {}", self.state_machine))?;
		let oracle_addr = Address::from_slice(&l2_oracle.0);
		let filter = Filter::new().address(oracle_addr).from_block(from).to_block(to);

		let logs = self.beacon_execution_client.get_logs(&filter).await?;

		let mut events: Vec<L2OutputOracle::OutputProposed> = logs
			.into_iter()
			.filter_map(|log| L2OutputOracle::OutputProposed::decode_log(&log.inner).ok())
			.map(|log| log.data)
			.collect();

		events.sort_unstable_by(|a, b| a.l2OutputIndex.cmp(&b.l2OutputIndex));

		Ok(events.last().cloned())
	}
```

**File:** evm/tests/foundry/SimplexPaymasterTest.t.sol (L245-263)
```text
    function testStaleOracleReverts() public {
        nativeOracle.setUpdatedAt(block.timestamp - paymaster.maxOracleAge() - 1);
        vm.expectRevert(
            abi.encodeWithSelector(
                SimplexPaymaster.StaleOraclePrice.selector,
                address(nativeOracle),
                block.timestamp - paymaster.maxOracleAge() - 1
            )
        );
        paymaster.getTokenPrice(address(usdc6));
    }

    function testNonPositiveOraclePriceReverts() public {
        usdcOracle.setAnswer(0);
        vm.expectRevert(
            abi.encodeWithSelector(SimplexPaymaster.InvalidOraclePrice.selector, address(usdcOracle), int256(0))
        );
        paymaster.getTokenPrice(address(usdc6));
    }
```
