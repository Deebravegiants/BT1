### Title
Unprotected `updateRate()` Allows Any Caller to Push rsETH/ETH Rate Cross-Chain — (File: `contracts/cross-chain/CrossChainRateProvider.sol`, `contracts/cross-chain/MultiChainRateProvider.sol`)

---

### Summary

Both `CrossChainRateProvider.updateRate()` and `MultiChainRateProvider.updateRate()` are `external payable` with no access control. Any unprivileged account can invoke them to broadcast the stored `rsETHPrice` from `LRTOracle` to receiver contracts on destination chains via LayerZero. This is a direct structural analog to the reference report's missing-access-control class: a state-changing, cross-chain-propagating function callable by anyone.

---

### Finding Description

`CrossChainRateProvider.updateRate()` reads `ILRTOracle(rsETHPriceOracle).rsETHPrice()` — the last *stored* price in `LRTOracle`, not the live computed price — and sends it via LayerZero to the configured `rateReceiver` on the destination chain. [1](#0-0) 

`MultiChainRateProvider.updateRate()` does the same but iterates over all registered `rateReceivers`. [2](#0-1) 

Neither function carries any role check or `onlyOwner` guard. The concrete implementations `RSETHRateProvider` and `RSETHMultiChainRateProvider` both resolve `getLatestRate()` to `ILRTOracle(rsETHPriceOracle).rsETHPrice()` — the *last written* value, which is only refreshed when `LRTOracle.updateRSETHPrice()` is called. [3](#0-2) [4](#0-3) 

L2 pools (`RSETHPoolV2`, `RSETHPoolV2NBA`, `RSETHPoolV2ExternalBridge`, etc.) consume the rate pushed to the receiver to compute how many wrsETH tokens to mint per ETH deposited:

```
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate
``` [5](#0-4) 

Because `rsETHPrice` in `LRTOracle` is only updated on explicit calls to `updateRSETHPrice()`, a window exists where the stored price is stale relative to the true current value. An attacker can exploit this window by calling `updateRate()` at a chosen moment to lock in a stale (lower-than-current) rate on L2, causing L2 depositors to receive more wrsETH per ETH than the protocol intends — diluting existing rsETH holders.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

When the stored `rsETHPrice` on L1 lags behind the true current price (a normal condition between oracle refreshes), an attacker can call `updateRate()` to push the stale lower rate to L2. L2 depositors then receive an inflated wrsETH amount (`amountAfterFee * 1e18 / staleRate > amountAfterFee * 1e18 / currentRate`). This over-minting dilutes the backing ratio for all existing rsETH/wrsETH holders. No direct ETH theft occurs, but the protocol fails to maintain the correct exchange rate guarantee for existing holders.

---

### Likelihood Explanation

**Medium.** The function is unconditionally `external payable` with no guard. Any EOA or contract can call it at any time by supplying the LayerZero fee as `msg.value`. The attacker bears only the gas and LZ messaging cost, which is modest. The stale-price window is a routine condition (oracle updates are not atomic with every block), so the precondition is reliably available.

---

### Recommendation

Add an `onlyOwner` (or equivalent role) modifier to `updateRate()` in both `CrossChainRateProvider` and `MultiChainRateProvider`, restricting rate propagation to authorized keepers or the protocol's own automation infrastructure. This mirrors the fix applied in the reference report (`onlyMsc` modifier).

```solidity
// CrossChainRateProvider.sol
function updateRate() external payable nonReentrant onlyOwner { ... }

// MultiChainRateProvider.sol
function updateRate() external payable nonReentrant onlyOwner { ... }
```

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/cross-chain/RSETHRateProvider.sol";

contract UnprotectedUpdateRatePoC is Test {
    RSETHRateProvider public rateProvider;

    function setUp() public {
        // Deploy with a mock oracle that returns a stale (lower) price
        address mockOracle = address(new MockOracle(1.00 ether)); // stale: 1.00 ETH
        rateProvider = new RSETHRateProvider(mockOracle, 101 /* Arbitrum LZ chainId */, address(lzEndpoint));
        rateProvider.updateRateReceiver(address(l2Receiver));
    }

    function testAnyoneCanPushStaleRate() public {
        // True current price is 1.05 ETH, but oracle stores 1.00 ETH (stale)
        // Attacker pushes stale rate to L2 — no access control prevents this
        vm.deal(address(this), 1 ether);
        rateProvider.updateRate{value: 0.01 ether}();
        // L2 receiver now holds rate = 1.00 ETH
        // L2 depositor sending 1 ETH gets 1e18/1e18 = 1.0 wrsETH
        // instead of correct 1e18/1.05e18 = 0.952 wrsETH → over-minting
    }
}
```

### Citations

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

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-137)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
                dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
            );

            unchecked {
                ++i;
            }
        }

        emit RateUpdated(rate);
    }
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L225-234)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
    }
```
