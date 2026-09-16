### Title
`SimplexPaymaster._getOraclePrice` Lacks Error Handling Around Chainlink `latestRoundData()`, Enabling Full DoS of Gas Sponsorship — ([File: evm/src/utils/SimplexPaymaster.sol])

### Summary
`SimplexPaymaster` is a permissionless ERC-4337 paymaster used by Hyperbridge's Simplex intent solvers to pay gas in stablecoins. Every `validatePaymasterUserOp` call for every token routes through `_getOraclePrice`, which calls the Chainlink `AggregatorV3Interface.latestRoundData()` directly with no `try/catch` and no fallback. If either the configured native/USD oracle or a token/USD oracle reverts for any reason (feed deprecated, access revoked, underlying aggregator paused, proxy pointing at a broken implementation), sponsorship for **every** registered token breaks, because `_tokenPrice` unconditionally queries `nativeOracle` before it queries the per-token oracle.

### Finding Description
`_getOraclePrice` is defined as: [1](#0-0) 

It is called unconditionally for both legs of every price computation in `_tokenPrice`: [2](#0-1) 

`_tokenPrice` is invoked from `_fetchDetails`, which runs during `validatePaymasterUserOp` for **every** UserOperation sponsored by this paymaster, regardless of which token the solver chose: [3](#0-2) 

Unlike the other external calls in this same contract — `_prefund`'s `PERMIT2.permitTransferFrom` and `_executePermit`'s `IERC20Permit.permit` — which are both wrapped in `try/catch` with a dedicated revert reason: [4](#0-3) [5](#0-4) 

the oracle call has no such protection. The existing test suite only covers stale/non-positive answers, never a reverting oracle call: [6](#0-5) 

This exactly mirrors the referenced report's bug class: unconditional reliance on `latestRoundData()` with no fallback logic, so denial of the feed (deprecation, access revocation, or an unexpected revert) permanently DoSes the dependent contract until an external, out-of-band remediation occurs.

### Impact Explanation
Because `nativeOracle` is read on every `_tokenPrice` call, a single broken feed — the native/USD oracle — disables `validatePaymasterUserOp` for **all** registered tokens simultaneously, not just the affected token. Any solver UserOperation submitted through this paymaster reverts during validation, so no gas sponsorship can be obtained via `SimplexPaymaster` on that chain until Hyperbridge governance delivers a `RegisterToken`/`UpdateParams` request through the full cross-chain governance round-trip (consensus proof + relayer delivery) to repoint the oracle. This is an unprivileged, permissionless entry point (any solver's UserOp reaching the EntryPoint) causing a chain-wide denial of a core protocol service (Simplex intent gas sponsorship) with no on-chain self-recovery.

### Likelihood Explanation
Chainlink feeds can revert for reasons outside the protocol's control: feed deprecation (Chainlink periodically deprecates and eventually blocks reads from old aggregators), an access-controlled aggregator revoking read access, or a faulty/paused underlying implementation. Given the multi-chain deployment (BSC, Base, Ethereum, Polygon, Arbitrum per the docs/config), the probability that at least one configured feed is deprecated or restricted over the contract's lifetime is non-trivial, and the trigger requires no attacker action — a single solver's ordinary UserOp submission surfaces the failure.

### Recommendation
Wrap both `latestRoundData()` calls in `_getOraclePrice` in `try/catch`, and either (a) fall back to a secondary oracle/price source, or (b) expose a governance-gated pause/deactivate path for the *native* oracle mirroring the existing per-token `active` flag, so a single broken native feed cannot deadlock sponsorship for every registered token while a fix is delivered through governance.

### Proof of Concept
1. Governance registers `nativeOracle` (e.g., BNB/USD) via `RegisterToken`/`UpdateParams`.
2. The underlying Chainlink aggregator later reverts on `latestRoundData()` (e.g., feed deprecated/access revoked — outside protocol control).
3. Any solver submits a UserOperation with `paymasterData` selecting any registered token (USDC, USDT, etc.).
4. `validatePaymasterUserOp` → `_fetchDetails` → `_tokenPrice` → `_getOraclePrice(nativeOracle, ...)` reverts with the aggregator's raw revert data (unhandled).
5. The EntryPoint's `validatePaymasterUserOp` call reverts, so the bundler drops the op; **every** solver op through this paymaster fails identically until governance repoints `nativeOracle`, which requires a full cross-chain consensus-proof-and-relay round trip.

### Citations

**File:** evm/src/utils/SimplexPaymaster.sol (L524-546)
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
```

**File:** evm/src/utils/SimplexPaymaster.sol (L594-607)
```text
        try PERMIT2.permitTransferFrom(
            ISignatureTransfer.PermitTransferFrom({
                permitted: ISignatureTransfer.TokenPermissions({token: tokenAddr, amount: permitAmount}),
                nonce: nonce,
                deadline: deadline
            }),
            ISignatureTransfer.SignatureTransferDetails({to: address(this), requestedAmount: prefundAmount}),
            owner,
            abi.encodePacked(r, s, v)
        ) {
            emit Permit2Executed(tokenAddr, owner, prefundAmount, nonce);
        } catch (bytes memory reason) {
            revert Permit2Failed(tokenAddr, reason);
        }
```

**File:** evm/src/utils/SimplexPaymaster.sol (L644-649)
```text
        try IERC20Permit(tokenAddr).permit(owner, address(this), permitAmount, deadline, v, r, s) {
            emit PermitExecuted(tokenAddr, owner, permitAmount);
        } catch {
            revert PermitFailed(tokenAddr);
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
