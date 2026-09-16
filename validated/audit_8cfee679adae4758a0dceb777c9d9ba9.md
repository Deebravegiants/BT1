## Title
Stale `feeToken()` re-read at escrow redemption can permanently freeze intent orders after a legitimate fee-token migration - (File: `evm/src/apps/intentsv2/IntentsBase.sol`)

### Summary
`IntentGatewayV2` escrows `order.fees` in whatever ERC-20 the host currently designates as `feeToken()` at order-placement time, but at redemption time it re-reads `feeToken()` fresh from the host rather than using the token that was actually escrowed. If governance rotates `EvmHost`'s `feeToken` via `updateHostParams` between order placement and redemption — an ordinary, sanctioned host-management action, exactly analogous to Hubble's `vusd` migration via `syncDeps()` — every pending order with `order.fees > 0` becomes permanently unredeemable, freezing not just the fee but the entire escrowed principal.

### Finding Description
At order placement, `IntentGatewayV2.placeOrder` reads the host's fee token, pulls `order.fees` of it into the gateway, and stores the raw amount under a sentinel key: [1](#0-0) 

At redemption, `IntentsBase._withdraw` (invoked from `onAccept`/`onGetResponse` for `RedeemEscrow`/`RefundEscrow`) re-fetches the host's *current* `feeToken()` and transfers the previously escrowed amount using that address: [2](#0-1) 

The tron-chain sibling contract has the identical pattern: [3](#0-2) 

The host's fee token is not immutable — `EvmHost.updateHostParams` (restricted to `hostManager`, driven by cross-chain governance requests) can freely change `feeToken`: [4](#0-3) 

The only guard against changing `feeToken` checks the **host's own** balance of the old token, not any downstream application's escrowed balance: [5](#0-4) 

This is precisely the `syncDeps()` bug class: a governance-controlled dependency address can change between a user's deposit and their later withdrawal, and the withdrawal path blindly trusts the *current* value of that dependency instead of the value that was actually in effect when funds were escrowed. `IntentGatewayV2`'s escrow of `order.fees` is entirely outside the host's own balance and thus invisible to the host's `CannotChangeFeeToken` check.

### Impact Explanation
`_withdraw`/`withdraw` releases the escrowed input tokens (`order.inputs`) and the escrowed fee (`TRANSACTION_FEES`) in the same atomic call. If the fee-token transfer reverts (because the gateway holds none of the newly-designated `feeToken`, which is the normal case after a migration), the whole `_withdraw` call reverts — which reverts the whole `onAccept`/`onGetResponse` handling of the `RedeemEscrow`/`RefundEscrow` message. Since the condition (host `feeToken` no longer equals what was escrowed) is persistent, every retry by the relayer fails identically. Both the escrowed principal (owed to the filler on `RedeemEscrow` or the user on `RefundEscrow`) and the escrowed relayer/protocol fee become permanently stuck — a genuine, unrecoverable freezing of user/solver funds, not merely an administrative inconvenience.

### Likelihood Explanation
Requires only a single, ordinary (non-malicious) governance action — rotating `feeToken`, an explicitly supported and documented operation (`HostParamsUpdated`, `CannotChangeFeeToken` docs) — occurring while any order with nonzero `order.fees` is in flight between placement and fill/redemption. Given cross-chain settlement latency (waiting for consensus proofs, challenge periods, relaying), there is a realistic window in which such a rotation could land between an order's placement and its redemption, affecting any solver or user with a pending order at that time.

### Recommendation
Escrow and later redeem fees using the token address recorded at placement time, not a live re-read of `feeToken()`. Store the specific ERC-20 address alongside the fee amount in `_orders[commitment]` (e.g. under a fee-token-specific key derived at placement), or track fees per concrete token like the `TokenInfo[]` array does for order inputs, so redemption never depends on `IDispatcher(host()).feeToken()` matching what was true when the order was placed.

### Proof of Concept
1. User places a cross-chain order via `IntentGatewayV2.placeOrder` with `order.fees = X` in `feeToken = TokenA`; the gateway now holds `X` `TokenA` and records `_orders[commitment][TRANSACTION_FEES] = X` (`evm/src/apps/IntentGatewayV2.sol:375-392`).
2. Before the order is filled/redeemed, Hyperbridge governance dispatches a `SetHostParam` action rotating the host's `feeToken` from `TokenA` to `TokenB` via `HostManager.onAccept` → `EvmHost.updateHostParams` (`evm/src/core/HostManager.sol:149-151`, `evm/src/core/EvmHost.sol:573-645`). This succeeds because the check only verifies the **host's** own `TokenA` balance is zero, not `IntentGatewayV2`'s.
3. A filler completes the order on the destination chain and the `RedeemEscrow` message is relayed back; `onAccept` calls `IntentsBase._withdraw`, which reads `feeToken() == TokenB` and attempts `IERC20(TokenB).safeTransfer(beneficiary, X)` (`evm/src/apps/intentsv2/IntentsBase.sol:472-477`).
4. The gateway holds `0` `TokenB`, so the transfer reverts, reverting the entire `_withdraw` call — including release of the escrowed `order.inputs` to the filler. The order can never be redeemed thereafter, permanently freezing both the fee and the principal escrow.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L375-392)
```text
        if (order.fees > 0) {
            address feeToken = IDispatcher(hostAddr).feeToken();
            if (msgValue > 0) {
                address uniswapV2 = IDispatcher(hostAddr).uniswapV2Router();
                address WETH = IUniswapV2Router02(uniswapV2).WETH();
                address[] memory path = new address[](2);
                path[0] = WETH;
                path[1] = feeToken;
                uint256[] memory amounts = IUniswapV2Router02(uniswapV2).swapETHForExactTokens{value: msgValue}(
                    order.fees, path, address(this), block.timestamp
                );
                msgValue -= amounts[0];
            } else {
                IERC20(feeToken).safeTransferFrom(msg.sender, address(this), order.fees);
            }

            _orders[commitment][TRANSACTION_FEES] = order.fees;
        }
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L472-477)
```text
        if (finalize) {
            uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
            if (fees > 0) {
                delete _orders[body.commitment][TRANSACTION_FEES];
                IERC20(IDispatcher(host()).feeToken()).safeTransfer(beneficiary, fees);
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L716-723)
```text
        // redeem tx fees
        uint256 fees = _orders[body.commitment][TRANSACTION_FEES];
        if (fees > 0) {
            address feeToken = IDispatcher(host()).feeToken();
            (bool success,) = feeToken.call(abi.encodeWithSelector(IERC20.transfer.selector, beneficiary, fees));
            if (!success) revert TransferFailed();
            delete _orders[body.commitment][TRANSACTION_FEES];
        }
```

**File:** evm/src/core/EvmHost.sol (L573-575)
```text
    function updateHostParams(HostParams memory params) external virtual restrict(_hostParams.hostManager) {
        updateHostParamsInternal(params);
    }
```

**File:** evm/src/core/EvmHost.sol (L617-621)
```text
        address oldFeeToken = feeToken();
        if (oldFeeToken != address(0) && oldFeeToken != params.feeToken) {
            uint256 balance = IERC20(oldFeeToken).balanceOf(address(this));
            if (balance != 0) revert CannotChangeFeeToken();
        }
```
