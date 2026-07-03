### Title
Stale Cross-Chain Rate in `AGETHRateReceiver` Causes `deposit()` to Under-Mint agETH to Depositors — (`contracts/agETH/AGETHPoolV3.sol`)

---

### Summary

`AGETHPoolV3.deposit()` computes the agETH amount to mint using a rate fetched from `AGETHRateReceiver` (a `CrossChainRateReceiver`). That receiver stores the last LayerZero-delivered rate in `rate` and records when it arrived in `lastUpdated`, but `getRate()` returns `rate` unconditionally — `lastUpdated` is never consulted. If the stored rate is stale and higher than the true current agETH/ETH rate, every depositor is minted fewer agETH than the current backing warrants.

---

### Finding Description

**Rate storage — `CrossChainRateReceiver`**

`lzReceive` writes the incoming rate and timestamp: [1](#0-0) 

`getRate()` returns the stored value with no age check: [2](#0-1) 

`lastUpdated` is a public field that is written but never read by any on-chain logic.

**Deposit math — `AGETHPoolV3`**

`deposit(string)` calls `viewSwapAgETHAmountAndFee`, which divides by the oracle rate:

```
agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
``` [3](#0-2) 

`getRate()` in the pool delegates directly to the oracle: [4](#0-3) 

`agETHOracle` is set to the `AGETHRateReceiver` instance at initialization: [5](#0-4) 

**The gap:** if the LayerZero message is delayed, dropped, or the rate has drifted downward since the last update, the stored rate can be higher than the true rate. Because `agETHAmount` is inversely proportional to the rate, a stale-high rate produces a smaller mint than the depositor is owed.

---

### Impact Explanation

Depositors send ETH and receive fewer agETH than the current agETH/ETH backing justifies. The ETH is not lost — it remains in the pool — but the depositor's position is immediately worth less than what they paid. This matches the **Low** scope: *contract fails to deliver promised returns, but doesn't lose value*.

---

### Likelihood Explanation

agETH is a yield-bearing token whose rate normally increases monotonically, so a stale-high rate requires either a temporary rate correction, a slashing event, or a prolonged LayerZero outage that freezes the rate while the true rate falls. LayerZero message delays and outages are documented operational risks. The `lastUpdated` field being present but unused confirms the staleness guard was anticipated but never implemented.

---

### Recommendation

Add a maximum staleness threshold and revert (or pause deposits) when the rate is too old:

```solidity
uint256 public constant MAX_RATE_AGE = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
    return rate;
}
```

Alternatively, expose `lastUpdated` to `AGETHPoolV3` and enforce the check there before minting.

---

### Proof of Concept

```solidity
// Fork test (Scroll or Linea, block where agETH rate is known)
function testStalehighRateUnderMints() public {
    // 1. Deploy or reference AGETHRateReceiver
    AGETHRateReceiver receiver = AGETHRateReceiver(<deployed_address>);

    // 2. Simulate a stale rate 5% above the true rate
    uint256 trueRate = receiver.getRate();          // e.g. 1.05e18
    uint256 staleRate = trueRate * 105 / 100;       // 1.1025e18

    // Overwrite storage slot for `rate` (slot 0 in CrossChainRateReceiver)
    vm.store(address(receiver), bytes32(0), bytes32(staleRate));
    // lastUpdated is NOT updated — staleness is invisible to the pool

    // 3. Deposit 1 ETH
    uint256 agETHBefore = agETH.balanceOf(alice);
    vm.prank(alice);
    pool.deposit{value: 1 ether}("");
    uint256 minted = agETH.balanceOf(alice) - agETHBefore;

    // 4. Expected amount at true rate (ignoring fee for clarity)
    uint256 expected = 1 ether * 1e18 / trueRate;

    // 5. Minted is less than expected — depositor is underpaid
    assertLt(minted, expected);
}
```

The test passes on unmodified code because `getRate()` in `CrossChainRateReceiver` returns `rate` without checking `lastUpdated`. [2](#0-1) [6](#0-5)

### Citations

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

**File:** contracts/agETH/AGETHPoolV3.sol (L97-99)
```text
        agETH = IERC20AgETH(_agETH);
        feeBps = _feeBps;
        agETHOracle = _agETHOracle;
```

**File:** contracts/agETH/AGETHPoolV3.sol (L104-106)
```text
    function getRate() public view returns (uint256) {
        return IOracle(agETHOracle).getRate();
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

**File:** contracts/agETH/AGETHPoolV3.sol (L160-168)
```text
    function viewSwapAgETHAmountAndFee(uint256 amount) public view returns (uint256 agETHAmount, uint256 fee) {
        fee = amount * feeBps / 10_000;
        uint256 amountAfterFee = amount - fee;

        // rate of agETH in ETH
        uint256 agETHToETHrate = getRate();

        // Calculate the final agETH amount
        agETHAmount = amountAfterFee * 1e18 / agETHToETHrate;
```
