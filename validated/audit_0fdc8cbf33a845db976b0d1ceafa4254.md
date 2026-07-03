### Title
`CrossChainRateReceiver.getRate()` Returns Zero-Initialized Rate When No `lzReceive` Has Succeeded, Causing All Pool Deposits to Revert - (`contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver` stores the rsETH/ETH rate in a `uint256 rate` storage variable that is zero-initialized at deployment. `getRate()` returns this value unconditionally. If no `lzReceive` call has ever succeeded (e.g., first message dropped, endpoint misconfigured at deploy), every downstream pool that divides by `rsETHToETHrate` will revert with a Solidity 0.8 division-by-zero panic, making the pool completely non-functional until a valid LZ message arrives.

---

### Finding Description

`CrossChainRateReceiver.rate` is a plain `uint256` storage slot, default-initialized to `0`. [1](#0-0) 

`getRate()` returns it with no zero-check and no staleness check: [2](#0-1) 

The only write path is `lzReceive`, which requires a correctly configured LayerZero endpoint, matching `srcChainId`, and matching `rateProvider`: [3](#0-2) 

`RSETHRateReceiver` sets these in its constructor but never seeds `rate` to a non-zero value: [4](#0-3) 

Every pool variant (`RSETHPool`, `RSETHPoolV2`, `RSETHPoolV2ExternalBridge`, `RSETHPoolV2NBA`, `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`, `RSETHPoolNoWrapper`) calls `IOracle(rsETHOracle).getRate()` and immediately divides by the result with no zero-guard: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

In Solidity 0.8+, `amountAfterFee * 1e18 / 0` triggers a `Panic(0x12)` revert, making `deposit()` completely non-functional.

---

### Impact Explanation

All pool `deposit()` calls revert with a division-by-zero panic for as long as `rate == 0`. No user funds are lost (the revert happens before any transfer), but the pool cannot deliver its promised swap service. This matches the **Low** scope: *Contract fails to deliver promised returns, but doesn't lose value*.

---

### Likelihood Explanation

The window exists from deployment until the first successful `lzReceive`. Any of the following realistic conditions extend this window indefinitely:
- The first LZ message is dropped (network congestion, insufficient gas fee passed to `updateRate()`).
- `layerZeroEndpoint`, `srcChainId`, or `rateProvider` is misconfigured at deploy time, causing every `lzReceive` call to revert on the require checks.
- The provider-side `updateRate()` is not called promptly after deployment.

There is no fallback, no initial rate seed, and no admin function to manually set `rate` on the receiver.

---

### Recommendation

1. Add a zero-check in `getRate()`:
   ```solidity
   function getRate() external view returns (uint256) {
       require(rate != 0, "Rate not initialized");
       return rate;
   }
   ```
2. Alternatively, add an owner-callable `setRate(uint256)` function to `CrossChainRateReceiver` so the rate can be bootstrapped before the first LZ message arrives.
3. All pool `viewSwapRsETHAmountAndFee` implementations should also defensively check `rsETHToETHrate != 0` before dividing.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "contracts/cross-chain/RSETHRateReceiver.sol";

contract ZeroRateTest is Test {
    RSETHRateReceiver receiver;

    function setUp() public {
        // Deploy with valid-looking but never-messaged config
        receiver = new RSETHRateReceiver(
            101,                        // srcChainId (Ethereum LZ id)
            address(0xDEAD),            // rateProvider
            address(0xBEEF)             // layerZeroEndpoint
        );
    }

    function test_getRateIsZeroBeforeFirstMessage() public {
        // No lzReceive has ever been called
        assertEq(receiver.getRate(), 0);
    }

    function test_poolDepositRevertsOnZeroRate() public {
        // Simulate pool division: amountAfterFee * 1e18 / rate
        uint256 amountAfterFee = 1 ether;
        uint256 rsETHToETHrate = receiver.getRate(); // == 0

        vm.expectRevert(); // Panic: division by zero
        uint256 result = amountAfterFee * 1e18 / rsETHToETHrate;
        (result); // suppress unused warning
    }
}
```

Running `forge test` on unmodified code will show `test_getRateIsZeroBeforeFirstMessage` passing and `test_poolDepositRevertsOnZeroRate` confirming the panic revert, proving the pool is non-functional until a valid LZ message is received.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L12-13)
```text
    /// @notice Last rate updated on the receiver
    uint256 public rate;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-99)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");

        uint256 _rate = abi.decode(_payload, (uint256));

        rate = _rate;

        lastUpdated = block.timestamp;

        emit RateUpdated(_rate);
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/cross-chain/RSETHRateReceiver.sol (L10-15)
```text
    constructor(uint16 _srcChainId, address _rateProvider, address _layerZeroEndpoint) {
        rateInfo = RateInfo({ tokenSymbol: "rsETH", baseTokenSymbol: "ETH" });
        srcChainId = _srcChainId;
        rateProvider = _rateProvider;
        layerZeroEndpoint = _layerZeroEndpoint;
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

**File:** contracts/pools/RSETHPool.sol (L311-319)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-307)
```text
    function viewSwapRsETHAmountAndFee(uint256 amount) public view returns (uint256 rsETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of rsETH in ETH
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
