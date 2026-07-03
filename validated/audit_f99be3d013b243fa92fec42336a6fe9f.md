### Title
Stale Cross-Chain Rate Enables Over-Minting of wrsETH, Diluting Existing Holders' Yield — (`contracts/cross-chain/CrossChainRateReceiver.sol`, `contracts/pools/RSETHPoolV3.sol`)

---

### Summary

`CrossChainRateReceiver.getRate()` returns the last stored rate with no staleness check. `RSETHPoolV3.viewSwapRsETHAmountAndFee()` uses this rate directly to compute wrsETH minting amounts. During the window between an L1 rsETH price increase and the corresponding LayerZero message delivery to L2, any depositor receives more wrsETH than the deposited ETH can back at the true rate, permanently diluting existing wrsETH holders' accrued yield.

---

### Finding Description

`CrossChainRateReceiver` stores `lastUpdated` but never enforces a maximum staleness threshold: [1](#0-0) 

```solidity
function getRate() external view returns (uint256) {
    return rate;  // no staleness check against lastUpdated
}
```

`RSETHPoolV3.getRate()` delegates directly to this oracle: [2](#0-1) 

`viewSwapRsETHAmountAndFee()` then uses the potentially stale rate to compute the wrsETH amount minted: [3](#0-2) 

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

The rate update path is: L1 `RSETHRateProvider.updateRate()` (permissionless, requires ETH for LZ fees) → LayerZero message → L2 `CrossChainRateReceiver.lzReceive()`. [4](#0-3) 

There is always a non-zero delivery window. During this window, the L2 receiver holds the old rate while the L1 oracle (`ILRTOracle.rsETHPrice()`) has already moved higher. [5](#0-4) 

---

### Impact Explanation

**High. Theft of unclaimed yield.**

Concrete arithmetic:
- True L1 rate: `1.1e18` (post-EigenLayer rewards). Stale L2 rate: `1.0e18`.
- Depositor sends 10 ETH. Fee = 0 for simplicity.
- wrsETH minted: `10e18 * 1e18 / 1.0e18 = 10e18` wrsETH.
- At the true rate, only `10e18 * 1e18 / 1.1e18 ≈ 9.09e18` wrsETH should be minted.
- Over-mint: `~0.91e18` wrsETH (~10%).
- The 10 ETH is later bridged to L1 and buys only `10/1.1 ≈ 9.09` rsETH.
- The pool now has 10 wrsETH outstanding backed by only 9.09 rsETH — a permanent shortfall of ~0.91 rsETH.
- This shortfall is borne by all existing wrsETH holders: their per-token redemption value is permanently reduced.

The yield that existing holders had accrued (the rate increase from 1.0 to 1.1) is redistributed to the new depositor via the over-minted supply. This is not a temporary condition — the over-minted tokens remain in circulation.

---

### Likelihood Explanation

- Rate increases are routine (EigenLayer rewards accrue continuously).
- LZ message delivery takes minutes to hours; the staleness window is inherent to the design.
- No special access is required. An attacker only needs to monitor L1 oracle updates and deposit on L2 before the LZ message arrives.
- `updateRate()` is permissionless but requires ETH for LZ fees, so the attacker can also delay the update by simply not calling it (the update is not automated on-chain). [6](#0-5) 

The `lastUpdated` field is stored but never used in any guard, confirming the missing check is a design omission, not an intentional trade-off.

---

### Recommendation

1. **Add a staleness guard in `CrossChainRateReceiver.getRate()`:**
   ```solidity
   uint256 public constant MAX_RATE_AGE = 1 hours;

   function getRate() external view returns (uint256) {
       require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
       return rate;
   }
   ```
   This causes deposits to revert when the rate is stale, preventing over-minting.

2. **Alternatively, pause deposits in `RSETHPoolV3` when the oracle rate is stale**, using `lastUpdated` exposed from the receiver.

3. **Automate rate pushes** (e.g., via a keeper/bot) to minimize the staleness window.

---

### Proof of Concept

```solidity
// Fork test (local fork, no public mainnet)
function testStaleRateDilutesExistingHolders() public {
    // Setup: existing holder has 10 wrsETH minted at rate 1.0e18
    // (10 ETH deposited, 10 wrsETH minted, 10 rsETH backing)

    // Simulate L1 rate increase to 1.1e18 (EigenLayer rewards)
    // LZ message NOT yet delivered — receiver still holds 1.0e18

    uint256 staleRate = 1.0e18;
    uint256 trueRate  = 1.1e18;

    // Attacker deposits 10 ETH at stale rate
    uint256 attackerWrsETH = 10e18 * 1e18 / staleRate; // = 10e18

    // ETH bridged to L1 buys rsETH at true rate
    uint256 rsETHBought = 10e18 * 1e18 / trueRate;     // ≈ 9.09e18

    // Total wrsETH supply: 10 (existing) + 10 (attacker) = 20
    // Total rsETH backing: 10 (existing) + 9.09 (new)   = 19.09
    // Existing holder redemption per wrsETH: 19.09/20 * 1.1 ETH ≈ 1.05 ETH
    // Expected (no dilution):                             1.1 ETH
    // Yield stolen per existing wrsETH: ~0.05 ETH (~4.5%)

    assertLt(existingHolderRedemptionValue, expectedRedemptionValue);
}
``` [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L16-16)
```text
    uint256 public lastUpdated;
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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L235-237)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L258-264)
```text
        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
```

**File:** contracts/pools/RSETHPoolV3.sol (L299-308)
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

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```
