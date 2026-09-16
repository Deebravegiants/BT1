### Title
Missing L2 sequencer-uptime check in `SimplexPaymaster._getOraclePrice` allows stale/manipulated Chainlink prices to mis-price gas payments and swaps - (File: evm/src/utils/SimplexPaymaster.sol)

### Summary
`SimplexPaymaster` is deployed on L2s (Base, Optimism, Arbitrum — see deployment addresses in `evm/script/SimplexPaymasterPermit2Probe.s.sol`) and prices ERC-20 gas payments and fee-recycling swaps purely from Chainlink `latestRoundData()`, checking only staleness (`updatedAt`) and positivity of the answer, with no L2 sequencer-uptime check as recommended by Chainlink for L2 deployments. [1](#0-0) 

### Finding Description
`_getOraclePrice` fetches `latestRoundData()` from the configured Chainlink feed and only validates `answer > 0` and `block.timestamp - updatedAt <= maxOracleAge`: [1](#0-0) 

This function backs both the per-UserOp gas pricing path (`_tokenPrice` → `_fetchDetails`, used during ERC-4337 validation/prefunding) and the permissioned `swapAndDeposit` fee-recycling swap: [2](#0-1) [3](#0-2) [4](#0-3) 

On Chainlink L2 feeds (Arbitrum, Optimism/Base, etc.), when the L2 sequencer goes down and later resumes, `updatedAt` can appear fresh (the feed itself may still be recently updated on L1 relay, or catches up quickly on sequencer restart) while the price reported does not yet reflect the true, potentially highly volatile market conditions during the outage. Because this contract lacks the standard `sequencerUptimeFeed`/grace-period check recommended by Chainlink for L2 oracle consumers, `_fetchDetails`/`_tokenPrice` and `swapAndDeposit` will accept and act on a price that is not actually trustworthy immediately after a sequencer restart.

The `_fetchDetails` path is reachable by any unprivileged party who can submit or bundle a UserOp through the paymaster (mode 0x00 permit or mode 0x02 Permit2), since token-price computation feeds directly into how many token units are pulled from the UserOp sender. [5](#0-4) 

### Impact Explanation
If the token/USD or native/USD price is stale/mispriced immediately after a sequencer outage:
- Gas-payment pricing (`_tokenPrice`) could undercharge or overcharge UserOp senders relative to true market rates, letting an attacker submit UserOps timed to the mispriced window to extract value from the paymaster's markup/treasury economics (e.g., paying far less token than the gas actually costs, draining the paymaster's native balance over repeated ops), or overcharging users.
- `swapAndDeposit`'s `amountOutMin` is derived from the same oracle path; a stale/incorrect price computed against a resumed-but-lagging feed could produce an `amountOutMin` that is far below the real market rate, allowing MEV/sandwich extraction of the treasury-triggered swap even though the function is `treasury`-gated (the treasury still relies on the on-chain price being accurate at broadcast time; a stale price during sequencer downtime removes that guarantee).

This is a Medium-severity oracle-integrity issue: it can lead to economic loss (mispriced gas draining the paymaster or overpaying users, and MEV-extractable slippage in `swapAndDeposit`) but requires the specific condition of an L2 sequencer outage/restart window to manifest, and the swap path additionally requires the treasury to trigger the swap during that window.

### Likelihood Explanation
Likelihood is moderate: it depends entirely on external L2 sequencer downtime events (which happen periodically on Arbitrum/Optimism/Base) coinciding with paymaster gas-payment or fee-recycling activity. It requires no privileged access and no special conditions beyond normal UserOp submission or the treasury calling `swapAndDeposit` shortly after a sequencer restart, both of which are part of the paymaster's ordinary/unprivileged operation.

### Recommendation
Add a Chainlink L2 sequencer-uptime feed check (per https://docs.chain.link/data-feeds/l2-sequencer-feeds) to `_getOraclePrice`, reverting if the sequencer is down or if it has been up for less than a configured grace period, before trusting `latestRoundData()` results in `_tokenPrice` and `swapAndDeposit`.

### Proof of Concept
1. Deploy `SimplexPaymaster` on Arbitrum/Optimism (as in `evm/script/SimplexPaymasterPermit2Probe.s.sol`, which targets Base Sepolia with live Chainlink feeds).
2. Simulate an L2 sequencer outage followed by restart; the Chainlink feed's `latestRoundData()` reports an `updatedAt` within `maxOracleAge` but reflects a price that predates the resumption of accurate sequencer-fed updates.
3. Submit a UserOp using mode 0x00/0x02 paymasterData during this window; `_fetchDetails`→`_tokenPrice`→`_getOraclePrice` accepts the stale/inaccurate price (passes both `answer > 0` and staleness checks) and computes `tokenPrice`, letting the attacker pay a token amount that does not reflect true gas cost.
4. Alternatively, have the treasury call `swapAndDeposit` during the same window; `expectedWei`/`amountOutMin` are derived from the same inaccurate price, allowing a bot to sandwich the resulting `swapExactTokensForETH` call for value extraction. [4](#0-3)

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L454-480)
```text
    function swapAndDeposit(address token, uint256 amountIn) external {
        if (msg.sender != treasury) revert UnauthorizedCall();
        address router = IDispatcher(host()).uniswapV2Router();
        if (router == address(0)) revert InvalidRouter(router);
        TokenConfig memory cfg = tokenConfigs[token];
        if (address(cfg.tokenOracle) == address(0)) revert TokenNotRegistered(token);

        uint256 balance = IERC20(token).balanceOf(address(this));
        if (amountIn == 0 || amountIn > balance) amountIn = balance;

        uint256 nativeUsd = _getOraclePrice(nativeOracle, nativeOracleDecimals);
        uint256 tokenUsd = _getOraclePrice(cfg.tokenOracle, cfg.tokenOracleDecimals);
        uint256 expectedWei = (amountIn * tokenUsd * 1e18) / (nativeUsd * (10 ** cfg.tokenDecimals));
        uint256 amountOutMin = (expectedWei * (10_000 - swapSlippageBps)) / 10_000;

        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = IUniswapV2Router02(router).WETH();

        IERC20(token).forceApprove(router, amountIn);
        uint256[] memory amounts = IUniswapV2Router02(router)
            .swapExactTokensForETH(amountIn, amountOutMin, path, address(this), block.timestamp);

        uint256 deposited = address(this).balance;
        entryPoint().depositTo{value: deposited}(address(this));
        emit FeesRecycled(token, amountIn, amounts[1], deposited);
    }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L516-556)
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
