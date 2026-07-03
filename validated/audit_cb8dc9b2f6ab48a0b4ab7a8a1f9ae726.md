Audit Report

## Title
L2 Pool Deposits Use Stale Cross-Chain Rate During LayerZero Propagation Window — (`contracts/cross-chain/CrossChainRateReceiver.sol`, `contracts/pools/RSETHPoolV2.sol`)

## Summary
`CrossChainRateReceiver.getRate()` returns the stored `rate` with no staleness check, despite recording `lastUpdated` on every update. Because `LRTOracle.updateRSETHPrice()` (L1) and `CrossChainRateProvider.updateRate()` (L1→L2 via LayerZero) are separate permissionless calls with inherent cross-chain delivery latency, all three L2 pool contracts (`RSETHPoolV2`, `RSETHPoolV2NBA`, `RSETHPoolV2ExternalBridge`) will mint wrsETH at the old (lower) rate during the propagation window, delivering more wrsETH than the updated rate warrants and diluting existing holders.

## Finding Description

**Rate update path (confirmed in code):**

1. `LRTOracle.updateRSETHPrice()` is `public whenNotPaused` — callable by anyone. [1](#0-0) 

2. `CrossChainRateProvider.updateRate()` has no access control — callable by anyone willing to pay LayerZero gas. It reads `getLatestRate()`, sets `rate`/`lastUpdated` locally, and dispatches a LayerZero message. [2](#0-1) 

3. `CrossChainRateReceiver.lzReceive()` sets `rate = _rate` and `lastUpdated = block.timestamp` only when the LayerZero message arrives on L2. [3](#0-2) 

4. `CrossChainRateReceiver.getRate()` returns `rate` unconditionally — `lastUpdated` is stored but never validated against any maximum staleness window. [4](#0-3) 

5. All three pool contracts call `IOracle(rsETHOracle).getRate()` inside `viewSwapRsETHAmountAndFee()` with no staleness check, and compute `rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate`. [5](#0-4) [6](#0-5) [7](#0-6) 

**Why existing checks are insufficient:** The `paused` modifier on the pools and the `dailyMintLimit` in `RSETHPoolV2` do not address rate staleness. The `lastUpdated` field exists in `CrossChainRateReceiver` but is never read by any pool contract.

## Impact Explanation

When `rsETHPrice` increases from P1 → P2 on L1 but the L2 receiver still holds P1, a depositor receives `amountAfterFee * 1e18 / P1 > amountAfterFee * 1e18 / P2` wrsETH. The protocol collects the correct ETH but mints excess wrsETH, diluting all existing wrsETH holders proportionally to the rate delta. No ETH is lost by the protocol. This matches **Low: Contract fails to deliver promised returns, but doesn't lose value**.

## Likelihood Explanation

- `updateRSETHPrice()` is permissionless; any actor (including automated bots) can trigger a rate update on L1.
- `updateRate()` requires a separate call and LayerZero message delivery (minutes of latency minimum), creating a predictable, always-present window.
- The profit per deposit is bounded by the rate delta (typically small — daily staking yield), but the window recurs with every rate update and requires no special privileges.
- Any depositor who observes the L1 oracle update on-chain can exploit this without any privileged access.

## Recommendation

Add a `MAX_STALENESS` check in the L2 pool's `getRate()` or `viewSwapRsETHAmountAndFee()`:

```solidity
uint256 lastUpdated = ICrossChainRateReceiver(rsETHOracle).lastUpdated();
require(block.timestamp - lastUpdated <= MAX_STALENESS, "Rate too stale");
```

Alternatively, expose `lastUpdated` through the `IOracle` interface and enforce it in the deposit path, reverting or pausing deposits when the rate has not been refreshed within an acceptable window (e.g., 1–4 hours).

## Proof of Concept

**Minimal call sequence on unmodified production code:**

1. **L1**: Call `LRTOracle.updateRSETHPrice()` — `rsETHPrice` moves from P1 → P2 (P2 > P1, e.g., daily staking accrual).
2. **L1**: Do NOT call `CrossChainRateProvider.updateRate()`. `CrossChainRateReceiver.rate` on L2 remains P1.
3. **L2**: Call `RSETHPoolV2.deposit{value: X}("")`. Internally: `viewSwapRsETHAmountAndFee(X)` → `getRate()` → `IOracle(rsETHOracle).getRate()` → returns stale P1.
4. **L2**: Pool mints `X * 1e18 / P1` wrsETH. After propagation, the correct amount would be `X * 1e18 / P2 < X * 1e18 / P1`.
5. **Foundry fork test plan**: Fork an L2 (e.g., Arbitrum) at a block where `CrossChainRateReceiver.rate` = P1. Warp L1 time, call `updateRSETHPrice()` to set P2 > P1 (without calling `updateRate()`). Call `RSETHPoolV2.deposit()` and assert minted wrsETH equals `X * 1e18 / P1`, confirming excess over `X * 1e18 / P2`.

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-233)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV2NBA.sol (L124-132)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV2ExternalBridge.sol (L307-315)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
