### Title
Missing Minimum Output Slippage Guard in L2 Pool `deposit()` Functions - (File: `contracts/pools/RSETHPoolV3.sol`, `contracts/pools/RSETHPoolV3ExternalBridge.sol`, `contracts/pools/RSETHPoolV3WithNativeChainBridge.sol`, `contracts/pools/RSETHPoolNoWrapper.sol`)

---

### Summary

All L2 pool `deposit()` functions lack a `minRsETHAmount` parameter. Users have no on-chain protection against receiving fewer `wrsETH`/`rsETH` tokens than expected when the oracle rate changes between transaction submission and execution. The L1 `LRTDepositPool` already implements this guard, confirming the protocol is aware of the pattern but omitted it from every L2 pool variant.

---

### Finding Description

Every L2 pool contract exposes two public `deposit()` entry points — one for native ETH and one for supported LST tokens. Both compute the output amount via `viewSwapRsETHAmountAndFee()`, which reads the live oracle rate with `getRate()`, then immediately mints or transfers that amount to the caller with no floor check.

`RSETHPoolV3.deposit(string)` (lines 246–265): [1](#0-0) 

`RSETHPoolV3.deposit(address,uint256,string)` (lines 271–293): [2](#0-1) 

The same pattern is repeated verbatim in `RSETHPoolV3ExternalBridge`: [3](#0-2) 

In `RSETHPoolV3WithNativeChainBridge`: [4](#0-3) 

And in `RSETHPoolNoWrapper` (which transfers pre-minted rsETH OFT instead of minting wrsETH): [5](#0-4) 

The oracle rate consumed by `viewSwapRsETHAmountAndFee()` is the value stored in a `CrossChainRateReceiver` (e.g., `RSETHRateReceiver`), which is updated from L1 via LayerZero: [6](#0-5) 

The `updateRate()` function on the L1 provider side is **permissionless** — any caller can push the current on-chain rsETH price to L2: [7](#0-6) 

By contrast, the L1 `LRTDepositPool` already enforces a caller-supplied minimum: [8](#0-7) 

This asymmetry confirms the protocol understands the need for slippage protection on deposits but did not carry it through to any L2 pool.

---

### Impact Explanation

A depositor submitting a transaction based on the current stale L2 rate can receive materially fewer `wrsETH`/`rsETH` than they computed off-chain. Because `wrsETH` is minted 1:1 against rsETH and rsETH is the user's only claim on the bridged ETH, receiving fewer tokens means a smaller proportional claim on the underlying. The user cannot revert the transaction after the fact. This matches **Low — contract fails to deliver promised returns**.

---

### Likelihood Explanation

The rsETH/ETH rate increases continuously as EigenLayer staking rewards accrue. The L2 oracle rate is periodically stale between LayerZero updates. Because `updateRate()` is permissionless, any actor (including a searcher/MEV bot) can push a fresh, higher rate to L2 at any time. A pending user deposit visible in the public mempool (on chains without private mempools) can be front-run by a `updateRate()` call, causing the deposit to execute at the newly elevated rate and mint fewer tokens than the user anticipated. No privileged role is required for the triggering step.

---

### Recommendation

Add a `minRsETHAmount` parameter to every `deposit()` overload in all four L2 pool contracts, mirroring the existing guard in `LRTDepositPool._beforeDeposit()`:

```solidity
// Example for RSETHPoolV3
function deposit(string memory referralId, uint256 minRsETHAmount)
    external payable nonReentrant whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    ...
    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minRsETHAmount) revert SlippageExceeded();
    ...
}
```

Apply the same pattern to the token-deposit overload and to `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, and `RSETHPoolNoWrapper`.

---

### Proof of Concept

1. The L2 `RSETHRateReceiver` holds a stale rate of **1.050 ETH/rsETH**; the true on-chain rate is **1.060 ETH/rsETH**.
2. Alice submits `deposit{value: 1 ether}("ref")` to `RSETHPoolV3`, expecting ≈ **0.952 wrsETH** (1 / 1.050).
3. A searcher observes Alice's pending transaction and calls `CrossChainRateProvider.updateRate()` on L1, paying enough gas to have the LayerZero message delivered to L2 before Alice's deposit.
4. `CrossChainRateReceiver.lzReceive()` updates the L2 rate to **1.060**.
5. Alice's deposit executes: `rsETHAmount = 1e18 * 1e18 / 1.060e18 ≈ 0.943 wrsETH` — **~0.009 wrsETH less** than expected.
6. Alice has no recourse; the contract accepted her ETH and minted fewer tokens with no minimum-output check.

The searcher need not profit directly; the structural absence of a slippage guard is sufficient for this outcome to occur naturally on every rate-update event.

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L258-263)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

```

**File:** contracts/pools/RSETHPoolV3.sol (L284-292)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L377-384)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L294-300)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L237-243)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-99)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
```

**File:** contracts/cross-chain/CrossChainRateProvider.sol (L85-101)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceiver, address(this));

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        ILayerZeroEndpoint(layerZeroEndpoint).send{ value: msg.value }(
            dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
        );

        emit RateUpdated(rate);
    }
```

**File:** contracts/LRTDepositPool.sol (L665-669)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
```
