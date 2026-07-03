Let me check the L2 pool contracts that consume `getRate()` to confirm the pricing impact.

### Title
Permissionless `updateRSETHPrice()` and `CrossChainRateProvider.updateRate()` can be blocked via block stuffing, causing stale rsETH rate on L2 receivers — (`contracts/interfaces/ILRTOracle.sol`, `contracts/cross-chain/CrossChainRateProvider.sol`, `contracts/cross-chain/RSETHRateProvider.sol`)

---

### Summary

Both `LRTOracle.updateRSETHPrice()` and `CrossChainRateProvider.updateRate()` are permissionless. An attacker can block-stuff Ethereum mainnet to prevent both from executing, keeping `rsETHPrice` stale in `LRTOracle` and propagating that stale value to `RSETHRateReceiver.rate` on destination chains. L2 pool contracts (`RSETHPoolV3`, `RSETHPoolV3WithNativeChainBridge`) consume `getRate()` with no staleness guard, so deposits and swaps are priced at the stale rate for the duration of the stuffing.

---

### Finding Description

**Permissionless update functions with no staleness protection:**

`LRTOracle.updateRSETHPrice()` carries only a `whenNotPaused` modifier — no role restriction: [1](#0-0) 

`CrossChainRateProvider.updateRate()` carries only `nonReentrant` — no role restriction: [2](#0-1) 

`RSETHRateProvider.getLatestRate()` reads the stored `rsETHPrice` state variable directly: [3](#0-2) 

`CrossChainRateReceiver.getRate()` returns the stored `rate` with no staleness check: [4](#0-3) 

L2 pool contracts consume this rate directly for deposit/swap pricing: [5](#0-4) 

**Attack path:**

1. Attacker block-stuffs Ethereum mainnet (fills blocks with high-priority transactions), preventing `updateRSETHPrice()` from being included.
2. During the stuffing window, staking rewards accrue → true rsETH/ETH rate rises, but `LRTOracle.rsETHPrice` remains at the pre-stuffing value.
3. Attacker (or anyone) calls `CrossChainRateProvider.updateRate()` — this reads the stale `rsETHPrice` and sends it via LayerZero to `RSETHRateReceiver`.
4. `RSETHRateReceiver.rate` is now set to the stale (lower) value on the destination chain.
5. L2 pool users depositing ETH receive more rsETH than the true rate warrants (since `rsETHAmount = ethIn / staleRate` where `staleRate < trueRate`), diluting existing rsETH holders.

---

### Impact Explanation

**Low. Block stuffing.** The stale rate on L2 receivers causes L2 pool contracts to misprice deposits and swaps for the duration of the stuffing. Users depositing during the window receive more rsETH than the true rate warrants, diluting existing holders. There is no permanent fund loss, but the protocol fails to deliver the correct exchange rate — matching the "Low. Contract fails to deliver promised returns" and "Low. Block stuffing." categories.

---

### Likelihood Explanation

Block stuffing Ethereum mainnet is expensive (each 30M-gas block at prevailing gas prices costs significant ETH), making sustained attacks economically irrational for small rate deviations. However, the technical path is fully concrete: both update functions are permissionless, neither the receiver nor the L2 pool has a staleness guard, and the rate discrepancy is directly exploitable by any depositor during the stuffing window.

---

### Recommendation

1. **Add a staleness check in `CrossChainRateReceiver.getRate()`**: revert or return a sentinel value if `block.timestamp - lastUpdated > MAX_STALENESS`.
2. **Add a staleness check in L2 pool `getRate()` consumers**: reject swaps/deposits if the oracle rate is older than an acceptable threshold.
3. **Decouple `updateRate()` from the stored `rsETHPrice`**: require that `updateRSETHPrice()` was called within the same block or within a recent window before `updateRate()` can propagate the value cross-chain.

---

### Proof of Concept

```solidity
// Fork test (Foundry) — mainnet + L2 state
// 1. Fork mainnet at block N; record rsETHPrice = P0
// 2. Roll forward 100 blocks without calling updateRSETHPrice()
//    (simulate block stuffing by simply not calling it)
// 3. Simulate TVL increase (e.g., warp time so staking rewards accrue,
//    or directly increase NodeDelegator balance in fork state)
// 4. Call CrossChainRateProvider.updateRate{value: fee}()
//    → this reads ILRTOracle.rsETHPrice() = P0 (stale)
//    → sends P0 to RSETHRateReceiver via LayerZero mock
// 5. On L2 fork: RSETHRateReceiver.rate == P0
// 6. Call LRTOracle.updateRSETHPrice() → rsETHPrice = P1 > P0
// 7. Assert: RSETHRateReceiver.rate (P0) != true rsETHPrice (P1)
// 8. Deposit ETH into RSETHPoolV3 on L2:
//    rsETHOut = ethIn * 1e18 / P0  >  ethIn * 1e18 / P1
//    → depositor receives excess rsETH at the expense of existing holders
``` [2](#0-1) [6](#0-5)

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

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
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

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L271-273)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```
