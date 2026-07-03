### Title
Missing `minOut` Guard in `RSETHPoolV2.deposit()` Allows Rate Drift to Reduce Received rsETH - (File: `contracts/pools/RSETHPoolV2.sol`)

---

### Summary

`RSETHPoolV2.deposit()` computes the rsETH output amount at execution time using the live oracle rate, but accepts no `minOut`/slippage parameter. Because `RSETHRateReceiver` (the oracle) stores a rate that is asynchronously updated via LayerZero's `lzReceive()`, the rate can change between when a user reads it off-chain and when their deposit transaction is mined, causing them to receive fewer rsETH tokens than they computed.

---

### Finding Description

`RSETHPoolV2.deposit()` contains no minimum-output guard: [1](#0-0) 

The output amount is computed entirely from the live oracle rate at execution time: [2](#0-1) 

The oracle (`RSETHRateReceiver`) stores a `rate` that is updated by any call to `lzReceive()` from the LayerZero endpoint: [3](#0-2) 

`RSETHPoolV2.getRate()` simply forwards to this stored value: [4](#0-3) 

Because rsETH is a yield-bearing token, its rate vs ETH monotonically increases over time. Every `lzReceive()` call pushes the rate higher. A user who reads `getRate()` at block N and submits a deposit will receive `amountAfterFee * 1e18 / rate_at_execution`, which is strictly less than what they computed if the rate was updated between submission and execution. There is no on-chain mechanism for the user to express a minimum acceptable output.

---

### Impact Explanation

The user receives fewer wrsETH tokens than the amount they computed when initiating the transaction. No funds are lost from the protocol — the ETH is still deposited and rsETH is still minted — but the user receives a worse-than-promised exchange. This matches the scoped impact: **Low. Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

LayerZero rate updates are routine protocol operations and occur independently of user transactions. On any L2 with a mempool (e.g., Arbitrum, Optimism), a rate update `lzReceive()` call can be included in the same block or a block between a user's submission and inclusion. Because the rate only ever increases, every rate update that occurs after a user reads the rate but before their deposit executes will reduce their output. This is a normal, non-adversarial condition.

---

### Recommendation

Add a `minOut` parameter to `deposit()` and revert if the computed `rsETHAmount` falls below it:

```solidity
function deposit(string memory referralId, uint256 minOut)
    external payable nonReentrant whenNotPaused limitDailyMint(msg.value)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();

    (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);
    if (rsETHAmount < minOut) revert SlippageExceeded();

    feeEarnedInETH += fee;
    wrsETH.mint(msg.sender, rsETHAmount);
    emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
}
```

---

### Proof of Concept

```solidity
// Fork test (local fork of L2 deployment)
function test_rateUpdateReducesOutput() public {
    uint256 rateBefore = pool.getRate(); // e.g. 1.05e18

    // Simulate a LayerZero rate update (rate increases to 1.06e18)
    vm.prank(layerZeroEndpoint);
    rateReceiver.lzReceive(
        srcChainId,
        abi.encodePacked(rateProvider),
        0,
        abi.encode(1.06e18)
    );

    uint256 rateAfter = pool.getRate(); // 1.06e18
    assert(rateAfter > rateBefore);

    // User deposits 1 ETH — receives less than computed at rateBefore
    uint256 expectedAtOldRate = 1e18 * 1e18 / rateBefore;
    vm.deal(user, 1 ether);
    vm.prank(user);
    pool.deposit{value: 1 ether}("");

    uint256 received = wrsETH.balanceOf(user);
    // received < expectedAtOldRate, no revert, no recourse
    assert(received < expectedAtOldRate);
}
```

The test requires no admin compromise, no front-running, and no external protocol failure — only the normal operation of the LayerZero rate feed.

### Citations

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
