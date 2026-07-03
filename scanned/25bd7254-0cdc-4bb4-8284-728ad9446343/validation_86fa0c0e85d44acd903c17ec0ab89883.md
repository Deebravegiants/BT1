### Title
Unrestricted `FeeReceiver.sendFunds()` Allows Attacker to Manufacture Artificial Yield and Trigger Protocol Fee Minting — (`contracts/FeeReceiver.sol`, `contracts/LRTOracle.sol`)

---

### Summary

`FeeReceiver.sendFunds()` has no access control. Any caller can donate ETH to `FeeReceiver`, call `sendFunds()` to push it into `LRTDepositPool`, and immediately call the public `LRTOracle.updateRSETHPrice()`. The oracle treats the ETH balance increase as genuine yield and mints protocol fee rsETH to `PROTOCOL_TREASURY`, diverting value that should have accrued to rsETH holders.

---

### Finding Description

**Step 1 — No guard on `sendFunds()`** [1](#0-0) 

`sendFunds()` is declared `external` with no role modifier. Any EOA or contract can call it at any time.

**Step 2 — `receiveFromRewardReceiver()` is also unrestricted** [2](#0-1) 

No access control; the call from `sendFunds()` succeeds unconditionally, crediting the deposit pool's raw ETH balance.

**Step 3 — ETH TVL is the raw `address(this).balance`** [3](#0-2) 

`getETHDistributionData()` returns `address(this).balance` directly. Donated ETH is indistinguishable from genuine staking rewards.

**Step 4 — `updateRSETHPrice()` is public** [4](#0-3) 

Only gated by `whenNotPaused`; any unprivileged caller can invoke it.

**Step 5 — Fee is minted on any TVL increase, regardless of source** [5](#0-4) 

`rewardAmount = totalETHInProtocol - previousTVL` treats the donated ETH as yield. The fee is computed and rsETH is minted to `PROTOCOL_TREASURY`. [6](#0-5) 

---

### Impact Explanation

The attacker donates `D` ETH. Without the fee mechanism, all rsETH holders would benefit from the full price appreciation `D / rsethSupply`. With the attack, the treasury extracts `D × protocolFeeInBPS / 10_000` worth of ETH as newly minted rsETH, diluting the appreciation that should have gone to existing holders. The donated ETH remains in the protocol (the attacker loses it), but the treasury captures a fee on it — a transfer of yield from rsETH holders to the treasury triggered by an unprivileged actor.

---

### Likelihood Explanation

- No privileged role is required.
- The only precondition is that the oracle is unpaused (normal operating state).
- The `pricePercentageLimit` guard (`PriceAboveDailyThreshold`) can be bypassed by donating small amounts that keep the price increase within the configured threshold, or is entirely absent when `pricePercentageLimit == 0`.
- The `maxFeeMintAmountPerDay` cap limits per-day damage but does not prevent the attack; it can be repeated across days.

---

### Recommendation

1. Add an access-control modifier (e.g., `onlyRole(LRTConstants.MANAGER)`) to `FeeReceiver.sendFunds()`.
2. Optionally restrict `receiveFromRewardReceiver()` to the registered `FeeReceiver` address.
3. Consider snapshotting the deposit pool's ETH balance at the time of the last price update and computing yield only against that snapshot, rather than the live raw balance.

---

### Proof of Concept

```solidity
// Foundry test (local fork or mock setup)
function testDonationFeeExploit() public {
    // Setup: protocol has 100 ETH TVL, rsETH supply = 100e18, price = 1e18
    // protocolFeeInBPS = 1000 (10%), pricePercentageLimit = 0 (disabled)

    address attacker = makeAddr("attacker");
    vm.deal(attacker, 1 ether);

    uint256 treasuryBalanceBefore = rsETH.balanceOf(treasury);

    vm.startPrank(attacker);
    // Step 1: donate 1 ETH to FeeReceiver
    (bool ok,) = address(feeReceiver).call{value: 1 ether}("");
    require(ok);

    // Step 2: push ETH into deposit pool — no access control
    feeReceiver.sendFunds();

    // Step 3: trigger fee minting — no access control
    lrtOracle.updateRSETHPrice();
    vm.stopPrank();

    uint256 treasuryBalanceAfter = rsETH.balanceOf(treasury);

    // Treasury received fee rsETH minted on the 1 ETH donation
    // rsETH holders lost ~0.1 ETH worth of yield to the treasury
    assertGt(treasuryBalanceAfter, treasuryBalanceBefore, "fee minted on donated ETH");
}
```

### Citations

**File:** contracts/FeeReceiver.sol (L53-58)
```text
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }
```

**File:** contracts/LRTDepositPool.sol (L61-61)
```text
    function receiveFromRewardReceiver() external payable { }
```

**File:** contracts/LRTDepositPool.sol (L480-480)
```text
        ethLyingInDepositPool = address(this).balance;
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
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
