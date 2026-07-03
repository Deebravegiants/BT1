### Title
Unguarded Payable Receiver Functions Allow Anyone to Inflate `totalETHInProtocol`, Causing Excess Protocol-Fee rsETH Minting and Diluting Existing Holder Yield - (`contracts/LRTDepositPool.sol`)

---

### Summary

Three payable functions on `LRTDepositPool` — `receiveFromRewardReceiver()`, `receiveFromNodeDelegator()`, and `receiveFromLRTConverter()` — carry no access control. Any caller can send ETH through them, inflating `address(this).balance`. Because `getETHDistributionData()` uses `address(this).balance` verbatim as `ethLyingInDepositPool`, and `LRTOracle._updateRsETHPrice()` reads this value to compute `totalETHInProtocol`, the donation is indistinguishable from legitimate staking yield. The oracle then computes `rewardAmount = totalETHInProtocol − previousTVL`, takes `protocolFeeInBPS` of it, and mints excess rsETH to the treasury — diluting the yield share of every existing rsETH holder.

---

### Finding Description

**Step 1 — Unguarded entry points.** [1](#0-0) 

All three functions are `external payable` with no role modifier, no `whenNotPaused`, and no caller validation. Any EOA or contract can call them with arbitrary ETH.

**Step 2 — Inflated balance flows into TVL.** [2](#0-1) 

`getETHDistributionData()` returns `address(this).balance` as `ethLyingInDepositPool`. There is no mechanism to distinguish ETH that arrived via a legitimate reward/node-delegator transfer from ETH sent by an arbitrary caller.

**Step 3 — Oracle reads the inflated TVL.** [3](#0-2) 

`_getTotalEthInProtocol()` calls `ILRTDepositPool.getTotalAssetDeposits(ETH_TOKEN)`, which ultimately returns the inflated `address(this).balance`.

**Step 4 — Excess fee is computed and minted.** [4](#0-3) 

`rewardAmount = totalETHInProtocol − previousTVL` is inflated by the donated ETH. `protocolFeeInETH = rewardAmount × protocolFeeInBPS / 10_000` is therefore larger than it should be. [5](#0-4) 

The excess fee is minted as rsETH to the treasury, diluting every existing holder.

---

### Impact Explanation

- **Existing rsETH holders** receive a smaller share of legitimate staking yield because the treasury is minted more rsETH than it earned.
- The attacker's donated ETH does become part of the protocol's backing (so rsETH price still rises), but the treasury captures `protocolFeeInBPS / 10_000` of the donation as an unearned fee, permanently diluting holders.
- The attack is repeatable each day up to `maxFeeMintAmountPerDay`.

---

### Likelihood Explanation

- The three functions are publicly callable with zero preconditions.
- `updateRSETHPrice()` is also public; the attacker can call it in the same transaction or front-run a legitimate oracle update.
- The attacker loses the donated ETH (not profitable), so the realistic actor is a griever or a party economically motivated to harm existing holders (e.g., a short position on rsETH).
- The `pricePercentageLimit` guard can revert if the donation is too large relative to TVL, but the attacker can calibrate the donation to stay within the threshold, or split it across multiple blocks.
- `maxFeeMintAmountPerDay` caps per-day damage but does not prevent the attack.

---

### Recommendation

Add a caller whitelist to the three receiver functions, restricting them to the legitimate contracts they are named after:

```solidity
modifier onlyRewardReceiver() {
    if (msg.sender != lrtConfig.getContract(LRTConstants.LRT_REWARD_RECEIVER))
        revert CallerNotRewardReceiver();
    _;
}

function receiveFromRewardReceiver() external payable onlyRewardReceiver { }
function receiveFromNodeDelegator() external payable {
    if (isNodeDelegator[msg.sender] == 0) revert CallerNotNodeDelegator();
}
function receiveFromLRTConverter() external payable {
    if (msg.sender != lrtConfig.getContract(LRTConstants.LRT_CONVERTER))
        revert CallerNotLRTConverter();
}
```

The bare `receive()` fallback should similarly be restricted or removed, as it provides the same inflation vector.

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import "forge-std/Test.sol";
import "../contracts/LRTDepositPool.sol";
import "../contracts/LRTOracle.sol";
import "../contracts/RSETH.sol";

contract ExcessFeeMintPoC is Test {
    LRTDepositPool depositPool;
    LRTOracle      oracle;
    RSETH          rseth;

    address attacker = address(0xBEEF);

    function setUp() public {
        // fork / deploy protocol as normal (omitted for brevity)
        // assume protocol has 1000 ETH TVL, rsETHPrice = 1.05e18, protocolFeeInBPS = 1000 (10%)
    }

    function testExcessFeeMint() public {
        // 1. Record state before attack
        uint256 supplyBefore   = rseth.totalSupply();
        uint256 priceBefore    = oracle.rsETHPrice();
        uint256 previousTVL    = (supplyBefore * priceBefore) / 1e18;
        uint256 treasuryBefore = rseth.balanceOf(treasury);

        // 2. Attacker donates 100 ETH via unguarded receiver
        vm.deal(attacker, 100 ether);
        vm.prank(attacker);
        depositPool.receiveFromRewardReceiver{value: 100 ether}();

        // 3. Oracle update (public — anyone can call)
        oracle.updateRSETHPrice();

        // 4. Treasury received excess fee rsETH
        uint256 treasuryAfter = rseth.balanceOf(treasury);
        uint256 legitimateYield = 0; // no real staking rewards in this block
        uint256 expectedFee = 0;     // should be 0 with no real yield

        // Assert treasury got more than expected
        assertGt(treasuryAfter - treasuryBefore, expectedFee,
            "Treasury minted excess rsETH from attacker donation");
    }
}
```

### Citations

**File:** contracts/LRTDepositPool.sol (L61-67)
```text
    function receiveFromRewardReceiver() external payable { }

    /// @dev receive from LRTConverter
    function receiveFromLRTConverter() external payable { }

    /// @dev receive from NodeDelegator
    function receiveFromNodeDelegator() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTOracle.sol (L244-247)
```text
        if (!protocolPaused && totalETHInProtocol > previousTVL) {
            uint256 rewardAmount = totalETHInProtocol - previousTVL;
            protocolFeeInETH = (rewardAmount * lrtConfig.protocolFeeInBPS()) / 10_000;
        }
```

**File:** contracts/LRTOracle.sol (L299-307)
```text
        if (protocolFeeInETH > 0) {
            // Calculate rsETH amount to mint as protocol fee
            uint256 rsethAmountToMintAsProtocolFee = protocolFeeInETH.divWad(newRsETHPrice);

            _checkAndUpdateDailyFeeMintLimit(rsethAmountToMintAsProtocolFee);
            if (rsethAmountToMintAsProtocolFee > 0) {
                address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
                IRSETH(rsETHTokenAddress).mint(treasury, rsethAmountToMintAsProtocolFee);
                emit FeeMinted(treasury, rsethAmountToMintAsProtocolFee);
```

**File:** contracts/LRTOracle.sol (L331-343)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);
```
