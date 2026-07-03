### Title
Zero-fee `withdrawFees` Proceeds Without State Change, Emitting Misleading Event - (File: contracts/pools/RSETHPool.sol)

### Summary
The `withdrawFees(address receiver)` and `withdrawFees(address receiver, address token)` functions across all L2 pool contracts lack a zero-amount guard. When called with no accumulated fees, they execute a zero-value transfer, emit a misleading `FeesWithdrawn(0)` event, and consume gas without changing any meaningful state — a direct analog to the `seizeInternal` zero-value no-op pattern.

### Finding Description
In `RSETHPool.sol`, `RSETHPoolV3.sol`, `RSETHPoolV3ExternalBridge.sol`, `RSETHPoolNoWrapper.sol`, and `RSETHPoolV3WithNativeChainBridge.sol`, the ETH fee withdrawal path reads `feeEarnedInETH`, zeroes it, then unconditionally executes a low-level ETH call:

```solidity
uint256 amountToSendInETH = feeEarnedInETH;
feeEarnedInETH = 0;
(bool success,) = payable(receiver).call{ value: amountToSendInETH }("");
if (!success) revert TransferFailed();
emit FeesWithdrawn(amountToSendInETH);
```

When `feeEarnedInETH == 0` at call time:
- `feeEarnedInETH = 0` is a no-op (already zero)
- `payable(receiver).call{ value: 0 }("")` is a zero-value ETH call
- `FeesWithdrawn(0)` is emitted — a misleading event indistinguishable from a real fee withdrawal

The same pattern exists for the token variant:

```solidity
uint256 amountToSendInToken = feeEarnedInToken[token];
feeEarnedInToken[token] = 0;
IERC20(token).safeTransfer(receiver, amountToSendInToken);
emit FeesWithdrawn(amountToSendInToken, token);
```

When `feeEarnedInToken[token] == 0`, a zero-value `safeTransfer` is executed and `FeesWithdrawn(0, token)` is emitted.

Affected locations:
- `RSETHPool.sol` lines 417–425 (ETH) and 428–443 (token)
- `RSETHPoolV3.sol` lines 453–461 (ETH) and 464–479 (token)
- `RSETHPoolV3ExternalBridge.sol` lines 617–625 (ETH) and 628–643 (token)
- `RSETHPoolNoWrapper.sol` lines 382–390 (ETH) and 393–408 (token)
- `RSETHPoolV3WithNativeChainBridge.sol` lines 487–495 (ETH) and 498–513 (token)

### Impact Explanation
The contract fails to deliver its promised behavior: a `FeesWithdrawn` event is emitted with a zero amount, which is semantically identical in structure to a real fee withdrawal event. Off-chain monitoring systems, dashboards, or accounting tools that rely on this event to track fee collection will record a spurious fee-withdrawal entry. No funds are lost, but the contract fails to deliver promised returns (a meaningful fee withdrawal) and produces observably incorrect accounting signals. **Impact: Low.**

### Likelihood Explanation
The `BRIDGER_ROLE` holder is expected to call `withdrawFees` on a regular operational schedule (e.g., daily or weekly). It is realistic that this call is made before any deposits have occurred, immediately after a prior withdrawal, or during a period of zero activity — all of which result in `feeEarnedInETH == 0`. No special conditions or attacker coordination are required; the no-op is triggered by ordinary operational usage.

### Recommendation
Add an early-return guard immediately after reading the fee balance, mirroring the fix recommended in the reference report:

```solidity
// ETH variant
uint256 amountToSendInETH = feeEarnedInETH;
if (amountToSendInETH == 0) return;
feeEarnedInETH = 0;
...

// Token variant
uint256 amountToSendInToken = feeEarnedInToken[token];
if (amountToSendInToken == 0) return;
feeEarnedInToken[token] = 0;
...
```

This prevents the zero-value transfer, suppresses the misleading event, and saves gas.

### Proof of Concept
1. Deploy any pool contract (e.g., `RSETHPoolV3`) with `feeBps = 0` or before any deposit occurs, so `feeEarnedInETH == 0`.
2. As `BRIDGER_ROLE`, call `withdrawFees(receiver)`.
3. The transaction succeeds. `feeEarnedInETH` remains `0`. A `FeesWithdrawn(0)` event is emitted. The receiver receives 0 ETH. Gas is consumed for a no-op.
4. Repeat for `withdrawFees(receiver, token)` with `feeEarnedInToken[token] == 0` to observe the same behavior for the token path.

<cite repo="Alyssadaypin/LRT-rsETH--011" path="contracts/pools/RSETHPool.sol" start="417" end="425