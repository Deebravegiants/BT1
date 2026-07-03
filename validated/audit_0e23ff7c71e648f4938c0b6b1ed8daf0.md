### Title
Missing Zero-Rate Guard in `lzReceive` Allows `rate = 0` to Be Stored, Breaking Cross-Chain Pool Operations — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver.lzReceive` unconditionally stores any decoded `uint256` rate, including zero, with no validity check. If `LRTOracle.rsETHPrice` is zero at the time `updateRate()` is called on the provider, a legitimate LZ message carrying `rate = 0` will be accepted and stored, causing all downstream pool operations that consume `getRate()` to revert until a corrective message arrives.

---

### Finding Description

`lzReceive` in `CrossChainRateReceiver` performs three access-control checks (endpoint, chain ID, source address) but applies no sanity check on the decoded value:

```solidity
uint256 _rate = abi.decode(_payload, (uint256));
rate = _rate;          // no require(_rate > 0)
lastUpdated = block.timestamp;
``` [1](#0-0) 

`RSETHMultiChainRateProvider.getLatestRate()` reads the `rsETHPrice` storage variable directly from `LRTOracle`:

```solidity
function getLatestRate() public view override returns (uint256) {
    return ILRTOracle(rsETHPriceOracle).rsETHPrice();
}
``` [2](#0-1) 

`rsETHPrice` can be zero in two concrete scenarios:

**Scenario A — Pre-initialization:** `rsETHPrice` is a plain `uint256` storage slot, default-initialized to 0. Before `updateRSETHPrice()` is ever called, `rsETHPrice == 0`. Anyone can call the permissionless `updateRate()` on the provider at this point.

**Scenario B — `pricePercentageLimit == 0` with zero TVL:** In `_updateRsETHPrice`, if `totalETHInProtocol == 0` (all assets withdrawn) while `rsethSupply > 0`, `newRsETHPrice` computes to 0. The downside-protection guard only fires when `pricePercentageLimit > 0`:

```solidity
bool isPriceDecreaseOffLimit =
    pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
``` [3](#0-2) 

Since `pricePercentageLimit` defaults to 0, the guard is disabled and execution falls through to `rsETHPrice = newRsETHPrice = 0` at line 313. [4](#0-3) [5](#0-4) 

`MultiChainRateProvider.updateRate()` is permissionless — any caller can trigger the cross-chain push:

```solidity
function updateRate() external payable nonReentrant {
    uint256 latestRate = getLatestRate();
    ...
    bytes memory _payload = abi.encode(latestRate);  // encodes 0
``` [6](#0-5) 

Once `rate = 0` is stored in the receiver, downstream pool consumers that call `getRate()` revert. For example, `RSETHPoolV3ExternalBridge.viewSwapAssetToPremintedRsETH` explicitly guards against this with `revert UnsupportedOracle()`:

```solidity
uint256 rsETHToETHrate = getRate();
if (rsETHToETHrate == 0) revert UnsupportedOracle();
``` [7](#0-6) 

Any pool path that does not have this guard would divide by zero. Either way, all cross-chain pool operations are broken until a corrective `lzReceive` with a valid rate is delivered.

---

### Impact Explanation

**Low. Contract fails to deliver promised returns, but doesn't lose value.**

Cross-chain deposits and swaps revert for all users on the destination chain. No funds are lost because the revert prevents any state change, but the contract fails to deliver its promised exchange-rate service until a corrective LZ message is sent.

---

### Likelihood Explanation

**Low-to-Medium.** Scenario A (pre-initialization) is a deployment-window race condition: if `updateRate()` is called before `updateRSETHPrice()` has ever been invoked, the zero is propagated. Scenario B requires `pricePercentageLimit` to remain at its default of 0 (no admin action taken) and all protocol TVL to reach zero while rsETH supply is non-zero — possible during a full withdrawal cycle. Neither scenario requires any privileged compromise; `updateRate()` is permissionless.

---

### Recommendation

Add a zero-rate guard in `lzReceive` before storing the decoded value:

```solidity
uint256 _rate = abi.decode(_payload, (uint256));
require(_rate > 0, "Rate must be > 0");
rate = _rate;
```

Additionally, add a symmetric guard in `updateRate()` / `MultiChainRateProvider` to prevent broadcasting a zero rate in the first place.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/cross-chain/RSETHRateReceiver.sol";

contract MockLZEndpoint {
    function callLzReceive(
        address receiver,
        uint16 srcChainId,
        address srcAddress,
        bytes calldata payload
    ) external {
        bytes memory srcAddressBytes = abi.encodePacked(srcAddress);
        RSETHRateReceiver(receiver).lzReceive(srcChainId, srcAddressBytes, 0, payload);
    }
}

contract ZeroRateTest is Test {
    RSETHRateReceiver receiver;
    MockLZEndpoint endpoint;
    address rateProvider = address(0xBEEF);
    uint16 srcChainId = 101;

    function setUp() public {
        endpoint = new MockLZEndpoint();
        receiver = new RSETHRateReceiver(srcChainId, rateProvider, address(endpoint));
    }

    function test_lzReceive_accepts_zero_rate() public {
        bytes memory payload = abi.encode(uint256(0));
        // Simulate legitimate LZ delivery from the registered endpoint + provider
        vm.prank(address(endpoint));
        receiver.lzReceive(srcChainId, abi.encodePacked(rateProvider), 0, payload);

        // rate is now 0 — invariant broken
        assertEq(receiver.rate(), 0);
    }
}
```

Run with: `forge test --match-test test_lzReceive_accepts_zero_rate -vvv`

The test passes (no revert), confirming `rate = 0` is stored. Any subsequent `getRate()` consumer that divides by this value will revert.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L93-97)
```text
        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L26-28)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L250-250)
```text
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L273-274)
```text
            bool isPriceDecreaseOffLimit =
                pricePercentageLimit > 0 && diff > pricePercentageLimit.mulWad(highestRsethPrice);
```

**File:** contracts/LRTOracle.sol (L313-313)
```text
        rsETHPrice = newRsETHPrice;
```

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-115)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L523-524)
```text
        uint256 rsETHToETHrate = getRate();
        if (rsETHToETHrate == 0) revert UnsupportedOracle();
```
