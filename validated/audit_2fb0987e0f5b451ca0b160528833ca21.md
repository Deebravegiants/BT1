### Title
Protocol Fee Effective Dilution Rate Depends on `updateRSETHPrice()` Call Frequency - (File: contracts/LRTOracle.sol)

### Summary
In `LRTOracle._updateRsETHPrice()`, the protocol fee is first computed in ETH terms as a percentage of TVL growth, then converted to rsETH at the current price for minting. Because the rsETH price is lower when the function is called more frequently (less reward has accumulated per call), more rsETH is minted per ETH of fee on each invocation. Over time, higher call frequency causes greater total rsETH dilution of existing holders than the nominal `protocolFeeInBPS` rate implies, while lower call frequency causes less dilution. The effective fee rate is therefore not deterministic and varies with call cadence.

### Finding Description
Inside `_updateRsETHPrice()`, the fee flow is:

```
rewardAmount       = totalETHInProtocol - previousTVL
protocolFeeInETH   = rewardAmount * protocolFeeInBPS / 10_000
newRsETHPrice      = (totalETHInProtocol - protocolFeeInETH) / rsethSupply
rsethFee           = protocolFeeInETH / newRsETHPrice   // ← price-dependent conversion
``` [1](#0-0) [2](#0-1) [3](#0-2) 

The ETH-denominated fee is identical regardless of call frequency (it is always `protocolFeeInBPS` of the incremental reward). However, the rsETH amount minted is `protocolFeeInETH / newRsETHPrice`. When the function is called more frequently, `newRsETHPrice` is lower at each call (less reward has compounded into the price), so the denominator is smaller and more rsETH is minted per ETH of fee. Across N calls covering the same total reward, the cumulative rsETH minted is strictly larger than across a single call covering the same reward, because the price used for conversion is lower on average.

`updateRSETHPrice()` carries no access control and is callable by any address: [4](#0-3) 

### Impact Explanation
Existing rsETH holders are diluted by the treasury's fee mint. The degree of dilution per unit of protocol reward is not fixed; it is higher when `updateRSETHPrice()` is called more frequently. The protocol therefore fails to deliver the exact promised fee rate to holders: the effective dilution rate is super-linear in call frequency rather than being a flat `protocolFeeInBPS` of rewards. No funds are lost outright, but holders receive fewer net rewards than the nominal fee parameter implies when the function is called at high cadence.

**Impact: Low — Contract fails to deliver promised returns, but doesn't lose value.**

### Likelihood Explanation
`updateRSETHPrice()` is a permissionless public function. Any external actor — including a depositor, rsETH holder, or bot — can call it at will. The protocol is expected to be called regularly by keeper bots, and the call frequency is not bounded on-chain. The condition is therefore always reachable by any unprivileged caller.

### Recommendation
Convert the fee to rsETH using the **pre-fee** price (i.e., `totalETHInProtocol / rsethSupply`) rather than the post-fee price, or compute the fee directly as a fixed rsETH share of the supply increase. Alternatively, adopt a continuous-compounding or fixed-period fee model so the effective rate is independent of call cadence, analogous to EIP-4626 streaming fee patterns.

### Proof of Concept
Assume `rsethSupply = 100`, initial `rsETHPrice = 1.0`, `protocolFeeInBPS = 1000` (10%), TVL grows from 100 → 120 ETH.

**Single call (TVL 100 → 120):**
- `rewardAmount = 20`, `protocolFeeInETH = 2`
- `newRsETHPrice = (120 − 2) / 100 = 1.18`
- `rsethFee = 2 / 1.18 ≈ 1.695 rsETH` minted

**Two calls (TVL 100 → 110, then 110 → 120):**

*Call 1:*
- `rewardAmount = 10`, `protocolFeeInETH = 1`
- `newRsETHPrice = (110 − 1) / 100 = 1.09`
- `rsethFee₁ = 1 / 1.09 ≈ 0.917 rsETH`; supply → 100.917

*Call 2:*
- `previousTVL = 100.917 × 1.09 ≈ 110`, `rewardAmount = 10`, `protocolFeeInETH = 1`
- `newRsETHPrice = (120 − 1) / 100.917 ≈ 1.1792`
- `rsethFee₂ = 1 / 1.1792 ≈ 0.848 rsETH`; supply → 101.765

**Result:** Two calls mint ≈ **1.765 rsETH** vs. one call minting ≈ **1.695 rsETH** — a ~4% increase in dilution for the same total reward, caused solely by higher call frequency. Any unprivileged caller can trigger this by repeatedly invoking `updateRSETHPrice()`. [5](#0-4)

### Citations

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L214-250)
```text
    function _updateRsETHPrice() internal {
        address rsETHTokenAddress = lrtConfig.rsETH();
        uint256 rsethSupply = IRSETH(rsETHTokenAddress).totalSupply();

        if (rsethSupply == 0) {
            rsETHPrice = 1 ether;
            highestRsethPrice = 1 ether;
            return;
        }

        if (highestRsethPrice == 0) {
            highestRsethPrice = rsETHPrice;
        }

        uint256 previousPrice = rsETHPrice;

        // get total ETH in the protocol (normalized to 1e18)
        uint256 totalETHInProtocol = _getTotalEthInProtocol();

        // calculate previousTVL using rsethSupply multiplied by rsETHPrice
        uint256 previousTVL = rsethSupply.mulWad(rsETHPrice);

        IPausable lrtDepositPool = IPausable(lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL));
        IPausable withdrawalManager = IPausable(lrtConfig.getContract(LRTConstants.LRT_WITHDRAW_MANAGER));

        // determine if the protocol is active (not paused)
        bool protocolPaused = lrtDepositPool.paused() || withdrawalManager.paused() || paused;

        // only take fee if TVL increased and protocol is not paused
        uint256 protocolFeeInETH = 0;
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }

        // compute new rsETH price based on total ETH minus fee
        uint256 newRsETHPrice = (totalETHInProtocol - protocolFeeInETH).divWad(rsethSupply);
```

**File:** contracts/LRTOracle.sol (L301-301)
```text
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);
```
