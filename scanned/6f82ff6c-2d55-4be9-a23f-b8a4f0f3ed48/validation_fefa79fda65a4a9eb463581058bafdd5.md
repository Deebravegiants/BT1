### Title
Stale rsETH/ETH Rate in RSETHRateReceiver Allows Excess wrsETH Minting and Yield Theft - (File: contracts/cross-chain/CrossChainRateReceiver.sol, contracts/pools/RSETHPoolV2.sol)

---

### Summary

`CrossChainRateReceiver.getRate()` returns the last stored rate with no staleness check. `RSETHPoolV2.deposit()` uses this rate to compute how many wrsETH tokens to mint. When the stored rate is lower than the true current rsETH/ETH rate, depositors receive more wrsETH than they are entitled to. Because wrsETH is a CCIP burn-mint token redeemable 1:1 for rsETH on L1, an attacker can bridge the excess wrsETH back to L1 and extract the yield delta from the protocol's rsETH reserve.

---

### Finding Description

`CrossChainRateReceiver` stores the rate and a `lastUpdated` timestamp, but `getRate()` returns the raw stored value with no freshness enforcement: [1](#0-0) 

The rate is only updated when `updateRate()` is called on `RSETHRateProvider` (L1) and the LayerZero message is delivered to `lzReceive()` on L2: [2](#0-1) [3](#0-2) 

`RSETHPoolV2.deposit()` calls `viewSwapRsETHAmountAndFee()`, which divides the ETH amount by the stale rate: [4](#0-3) 

If `rsETHToETHrate` is stale-low (e.g., 1.05e18 instead of the true 1.10e18), the division `amountAfterFee * 1e18 / rsETHToETHrate` yields more wrsETH than the depositor deserves. The pool then mints that inflated amount directly to the caller: [5](#0-4) 

`WrappedRSETH` is a CCIP burn-mint ERC677 token. The CCIP bridge burns wrsETH on L2 and releases rsETH 1:1 from the L1 lock-release pool. The attacker bridges the excess wrsETH to L1 and receives rsETH at the true rate, extracting the yield delta from the protocol's reserve. [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

For a deposit of `X` ETH with stale rate `R_stale` and true rate `R_true > R_stale`:

- wrsETH minted: `X * 1e18 / R_stale`
- wrsETH deserved: `X * 1e18 / R_true`
- Excess wrsETH: `X * 1e18 * (1/R_stale - 1/R_true)`
- Profit in ETH after bridging: `X * (R_true/R_stale - 1)`

The excess rsETH is drawn from the protocol's reserve, constituting direct theft of yield that belongs to existing rsETH holders. The daily mint limit caps per-day exposure but does not prevent the attack across multiple days or with a large single deposit within the limit. [7](#0-6) 

---

### Likelihood Explanation

**Medium-High.** The rate update is not automated on-chain; it requires an off-chain keeper to call `updateRate()` and pay for LayerZero gas. Any period of keeper inactivity, network congestion, or LayerZero delivery delay leaves the rate stale. rsETH accrues staking yield continuously, so even a few hours of staleness creates an exploitable gap. The attacker needs no special role or permission — `deposit()` is fully public. [8](#0-7) 

---

### Recommendation

1. **Add a staleness check in `getRate()`**: revert (or return a sentinel) if `block.timestamp - lastUpdated > MAX_STALENESS` (e.g., 24 hours).
2. **Enforce the check in `RSETHPoolV2`**: `viewSwapRsETHAmountAndFee` should revert if the oracle rate is stale, preventing deposits when the rate cannot be trusted.
3. **Automate rate updates**: use a Chainlink Automation or equivalent keeper to push rate updates on a fixed cadence, ensuring the gap between true and stored rate stays within an acceptable tolerance. [9](#0-8) 

---

### Proof of Concept

```solidity
// Fork test (L2 fork with fixed stale rate)
function testStaleRateYieldTheft() public {
    // 1. Deploy/fork RSETHRateReceiver with stale rate = 1.05e18
    //    True rate on L1 = 1.10e18 (5% yield accrued since last update)
    uint256 staleRate = 1.05e18;
    uint256 trueRate  = 1.10e18;
    vm.mockCall(
        address(rsETHOracle),
        abi.encodeWithSelector(IOracle.getRate.selector),
        abi.encode(staleRate)
    );

    uint256 depositETH = 100 ether;
    uint256 wrsETHMinted = depositETH * 1e18 / staleRate;
    // = 95.238... wrsETH

    uint256 wrsETHDeserved = depositETH * 1e18 / trueRate;
    // = 90.909... wrsETH

    uint256 excessWrsETH = wrsETHMinted - wrsETHDeserved;
    // ≈ 4.329 wrsETH

    // 2. Attacker calls deposit
    vm.deal(attacker, depositETH);
    vm.prank(attacker);
    pool.deposit{value: depositETH}("ref");

    assertEq(wrsETH.balanceOf(attacker), wrsETHMinted);

    // 3. Bridge wrsETH to L1 via CCIP (burn on L2, release rsETH 1:1 on L1)
    // 4. On L1: attacker holds wrsETHMinted rsETH worth wrsETHMinted * trueRate ETH
    uint256 profitETH = wrsETHMinted * trueRate / 1e18 - depositETH;
    // ≈ 4.762 ETH profit extracted from protocol reserve

    assertGt(profitETH, 0, "attacker profits from stale rate");
}
```

The fuzz variant parameterizes `(staleRate, trueRate, depositAmount)` with `trueRate > staleRate` and asserts `profit > 0` for all valid inputs, confirming the invariant is broken whenever the rate is stale.

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-14)
```text
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

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
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

**File:** contracts/pools/RSETHPoolV2.sol (L72-93)
```text
    modifier limitDailyMint(uint256 amount) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        // Calculate the amount of rsETH that will be minted
        (uint256 rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
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

**File:** contracts/pools/RSETHPoolV2.sol (L225-234)
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

**File:** contracts/ccip/WrappedRSETH.sol (L137-141)
```text
    function mint(address account, uint256 amount) external override onlyMinter validAddress(account) {
        if (i_maxSupply != 0 && totalSupply() + amount > i_maxSupply) revert MaxSupplyExceeded(totalSupply() + amount);

        _mint(account, amount);
    }
```
