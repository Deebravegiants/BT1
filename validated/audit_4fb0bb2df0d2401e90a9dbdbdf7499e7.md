### Title
Stale Rate in `CrossChainRateReceiver.getRate()` Allows Over-Minting of agETH — (`contracts/agETH/AGETHRateReceiver.sol` / `contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver` stores `lastUpdated` when a LayerZero message arrives but **never validates it** in `getRate()`. `AGETHPoolV3.deposit()` calls `getRate()` unconditionally, so any depositor who transacts while the cross-chain rate is stale receives more agETH than the current L1 backing rate justifies.

---

### Finding Description

`CrossChainRateReceiver.getRate()` simply returns the stored `rate` with no freshness guard: [1](#0-0) 

`lastUpdated` is written on every `lzReceive` call: [2](#0-1) 

But it is never read back or compared against any threshold anywhere in the contract.

`AGETHPoolV3.deposit()` calls `viewSwapAgETHAmountAndFee()`, which calls `getRate()` and uses the result directly in the mint calculation: [3](#0-2) 

The formula is:

```
agETHAmount = amountAfterFee * 1e18 / agETHToETHrate
```

If `agETHToETHrate` is stale and **lower** than the current L1 rate (agETH has appreciated since the last LZ message), the division yields a **larger** `agETHAmount` than the deposited ETH actually backs at the current rate. [4](#0-3) 

---

### Impact Explanation

Every depositor who calls `deposit()` during a period of LZ relay delay (while agETH has appreciated on L1) receives more agETH than their ETH is worth at the current rate. The minted agETH supply on L2 exceeds what the bridged ETH can back at the true rate, violating the full-backing invariant. This matches **Low — Contract fails to deliver promised returns, but doesn't lose value**: the deposited ETH remains in the pool, but the protocol over-issues agETH relative to the current exchange rate.

---

### Likelihood Explanation

LayerZero relay delays are a realistic operational condition (network congestion, relayer downtime, gas spikes). agETH accrues yield continuously on L1, so its rate increases monotonically over time. Any gap between `lzReceive` calls is a window where the stored rate is below the true rate. No special privileges are required — any unprivileged depositor benefits automatically.

---

### Recommendation

Add a staleness threshold check inside `CrossChainRateReceiver.getRate()` (or in `AGETHPoolV3.getRate()`). For example:

```solidity
uint256 public constant MAX_RATE_AGE = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
    return rate;
}
```

This causes deposits to revert when the oracle is stale, preventing over-minting until a fresh LZ message arrives.

---

### Proof of Concept

```solidity
// Fork test (L2 fork, e.g. Arbitrum)
function testStaleRateOverMint() public {
    // Simulate: last lzReceive set rate = 1.01e18 (old rate)
    // True current L1 rate = 1.02e18 (agETH appreciated)
    vm.store(address(rateReceiver), RATE_SLOT, bytes32(uint256(1.01e18)));
    vm.store(address(rateReceiver), LAST_UPDATED_SLOT, bytes32(block.timestamp - 7 days));

    uint256 depositAmount = 1 ether;
    uint256 agETHBefore = agETH.balanceOf(alice);

    vm.prank(alice);
    pool.deposit{value: depositAmount}("ref");

    uint256 agETHReceived = agETH.balanceOf(alice) - agETHBefore;
    uint256 correctAmount = depositAmount * 1e18 / 1.02e18; // at true rate

    // agETHReceived > correctAmount — over-minted
    assertGt(agETHReceived, correctAmount);
}
```

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L95-97)
```text
        rate = _rate;

        lastUpdated = block.timestamp;
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L115-128)
```text
    function deposit(string memory referralId) external payable nonReentrant {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
    }
```

**File:** contracts/agETH/AGETHPoolV3.sol (L160-169)
```text
    function viewSwapAgETHAmountAndFee(uint256 amount) public view returns (uint256 agETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
    }
```
