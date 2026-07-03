### Title
Stale Rate Accepted Without Freshness Check Enables Block-Stuffing-Assisted Over-Minting of wrsETH — (`contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver.getRate()` returns the last stored `rate` with no staleness guard. On low-cost L2 chains (Blast, Mode, Scroll), an attacker can perform block stuffing to delay the LayerZero relayer from landing `lzReceive`, keeping `rate` frozen at a stale (lower) value. Because `RSETHPoolV2` and `RSETHPoolV3` consume this rate directly in their deposit math, depositors receive more wrsETH per ETH than the current L1 backing justifies.

---

### Finding Description

`CrossChainRateReceiver.lzReceive` is the sole mechanism for updating `rate` and `lastUpdated` on the destination chain: [1](#0-0) 

`getRate()` returns `rate` unconditionally — there is no check against `lastUpdated` or any maximum staleness threshold: [2](#0-1) 

Both pool contracts delegate their rate lookup to this oracle without any freshness validation. In `RSETHPoolV2`: [3](#0-2) 

The minting math divides by the stale rate: [4](#0-3) 

The same pattern exists in `RSETHPoolV3`: [5](#0-4) 

**Attack path:**

1. On the L2 destination chain, the attacker submits enough high-gas dummy transactions to fill consecutive blocks, preventing the LayerZero relayer from including the `lzReceive` call.
2. While blocks are stuffed, `rate` remains frozen at the pre-stuffing value. As rsETH accrues staking yield on L1, the true rate rises, but the stored rate does not.
3. The attacker (and any other depositor) calls `deposit()`. Because `rsETHAmount = amountAfterFee * 1e18 / staleLowerRate`, they receive more wrsETH than the current L1 backing justifies.
4. Once stuffing stops, `lzReceive` lands and `rate` is updated, but the excess wrsETH has already been minted.

---

### Impact Explanation

The protocol mints wrsETH at a rate that no longer reflects the true L1 rsETH/ETH exchange rate. The minted wrsETH is undercollateralized relative to the ETH deposited, meaning the contract fails to deliver the promised 1:1 backing invariant. This falls under **Low — Block stuffing / contract fails to deliver promised returns**.

---

### Likelihood Explanation

On chains with low base fees (Blast, Mode, Scroll), the cost of filling blocks is substantially lower than on Ethereum mainnet. The attacker only needs to delay the relayer for the duration between two scheduled rate pushes (typically minutes to hours). The profit from minting excess wrsETH at a stale rate can offset the stuffing cost, especially for large deposits. No privileged role is required; `deposit()` is fully public. [6](#0-5) 

---

### Recommendation

Add a maximum staleness check inside `getRate()` (or in the pool's `viewSwapRsETHAmountAndFee`):

```solidity
uint256 public constant MAX_RATE_STALENESS = 1 hours;

function getRate() external view returns (uint256) {
    require(
        block.timestamp - lastUpdated <= MAX_RATE_STALENESS,
        "Rate is stale"
    );
    return rate;
}
```

This causes `deposit()` to revert when the rate has not been refreshed within the acceptable window, eliminating the economic incentive for block stuffing. [7](#0-6) 

---

### Proof of Concept

```solidity
// Fork test on a low-cost L2 (e.g., Blast)
function testBlockStuffingStaleRate() public {
    // 1. Record the current rate before stuffing
    uint256 rateBefore = crossChainRateReceiver.getRate();
    uint256 lastUpdatedBefore = crossChainRateReceiver.lastUpdated();

    // 2. Simulate block stuffing: advance time past the rate-push window
    //    without allowing lzReceive to land (no vm.prank(lzEndpoint) call)
    vm.warp(block.timestamp + 2 hours);
    vm.roll(block.number + 500); // ~500 full blocks on a 14s chain

    // 3. Rate is still the old (lower) value
    assertEq(crossChainRateReceiver.getRate(), rateBefore);
    assertGt(block.timestamp - lastUpdatedBefore, 1 hours); // staleness confirmed

    // 4. Deposit ETH and observe over-minting
    uint256 ethDeposit = 1 ether;
    (uint256 rsETHAmount,) = rsETHPoolV2.viewSwapRsETHAmountAndFee(ethDeposit);

    // Compute what the amount should be at the true (higher) L1 rate
    uint256 trueL1Rate = rateBefore + (rateBefore * 5 / 10_000); // ~5 bps yield accrual
    uint256 fee = ethDeposit * rsETHPoolV2.feeBps() / 10_000;
    uint256 correctAmount = (ethDeposit - fee) * 1e18 / trueL1Rate;

    // rsETHAmount > correctAmount: excess wrsETH minted
    assertGt(rsETHAmount, correctAmount);
}
``` [8](#0-7) [9](#0-8)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L12-16)
```text
    /// @notice Last rate updated on the receiver
    uint256 public rate;

    /// @notice Last time rate was updated
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

**File:** contracts/pools/RSETHPoolV2.sol (L201-203)
```text
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
    }
```

**File:** contracts/pools/RSETHPoolV2.sol (L207-218)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused limitDailyMint(msg.value) {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
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
