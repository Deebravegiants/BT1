### Title
Unbounded Staleness in `CrossChainRateReceiver.getRate()` Enables Over-Minting of wrsETH on L2 Pools — (File: `contracts/cross-chain/CrossChainRateReceiver.sol`)

---

### Summary

`CrossChainRateReceiver` records a `lastUpdated` timestamp every time a rate is pushed from L1 via LayerZero, but `getRate()` returns the stored `rate` unconditionally — it never checks `lastUpdated`. There is no staleness timeout. L2 deposit pools (`RSETHPoolV3`, `RSETHPoolNoWrapper`) call `getRate()` on every deposit to compute how much wrsETH/rsETH to mint. If the L2 oracle rate is stale and lower than the true L1 rate (i.e., rsETH has appreciated but the cross-chain message has not yet arrived or `updateRate()` has not been called), any depositor can mint more wrsETH than the current protocol rate entitles them to, diluting existing holders.

---

### Finding Description

`CrossChainRateReceiver.lzReceive()` stores both `rate` and `lastUpdated` on every successful update:

```solidity
rate = _rate;
lastUpdated = block.timestamp;
```

But `getRate()` ignores `lastUpdated` entirely:

```solidity
function getRate() external view returns (uint256) {
    return rate;
}
``` [1](#0-0) 

There is no maximum age enforced on the returned rate. The `lastUpdated` field is stored but never used for validation anywhere in the contract.

Both L2 pool variants call this oracle on every deposit:

```solidity
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [2](#0-1) [3](#0-2) 

If `rsETHToETHrate` is stale and lower than the true current rate (rsETH has appreciated on L1 but the L2 oracle has not been updated), the division yields a larger `rsETHAmount`, minting more wrsETH/rsETH than the depositor is entitled to.

The analog to the external report is exact: just as `resolveRegistration` could be called at any arbitrary time after voting ended — allowing a malicious actor to choose the most advantageous moment — here the rate can remain unresolved (stale) for an arbitrary duration with no on-chain enforcement, and any depositor can exploit the discrepancy the moment they observe it.

---

### Impact Explanation

**High — Theft of unclaimed yield.**

When a depositor mints wrsETH at a stale lower rate, they receive more shares than the current protocol backing justifies. The excess shares are backed by the same pool of underlying assets, diluting the share value for all existing wrsETH holders. The yield that existing holders have accrued (the appreciation of rsETH on L1) is partially transferred to the late depositor. This is a direct, quantifiable loss of yield for every existing wrsETH holder proportional to the size of the stale-rate deposit.

---

### Likelihood Explanation

**Medium.**

LayerZero message delays are a documented operational reality. The `updateRate()` call on `MultiChainRateProvider` is not automated on-chain — it is triggered off-chain by an admin or bot. Any lapse in that bot (downtime, gas exhaustion, network congestion) leaves the L2 oracle stale. rsETH appreciates continuously as EigenLayer staking rewards accrue, so the stale rate will almost always be lower than the true rate after any meaningful delay. A sophisticated depositor monitoring both L1 `LRTOracle.rsETHPrice` and the L2 `CrossChainRateReceiver.rate` can detect and exploit the discrepancy without any special privileges — only a standard `deposit()` call is required. [4](#0-3) [5](#0-4) 

---

### Recommendation

**Short term:** Add a staleness guard in `getRate()`:

```solidity
uint256 public constant MAX_RATE_AGE = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_RATE_AGE, "Rate is stale");
    return rate;
}
```

This mirrors the recommendation in the external report: add a hardcoded maximum age so that a rate that has not been refreshed within the window is rejected rather than silently consumed.

**Long term:** Automate `updateRate()` calls on L1 via a keeper or Chainlink Automation job so that the L2 oracle is refreshed on a fixed cadence (e.g., every 4–8 hours), and alert on any gap exceeding the staleness threshold.

---

### Proof of Concept

1. At time T, L1 `LRTOracle.rsETHPrice` = 1.05 ETH. `MultiChainRateProvider.updateRate()` is called; L2 `CrossChainRateReceiver.rate` = 1.05 ETH, `lastUpdated` = T.
2. EigenLayer rewards accrue. At time T+12h, L1 `rsETHPrice` = 1.10 ETH. The off-chain bot is down; `updateRate()` is not called. L2 oracle still returns 1.05 ETH.
3. Attacker observes the discrepancy by reading both on-chain values. Attacker calls `RSETHPoolV3.deposit{value: 1.05 ETH}("")`.
4. Pool computes: `rsETHAmount = 1.05e18 * 1e18 / 1.05e18 = 1.0 wrsETH`. At the true rate of 1.10 ETH/rsETH, 1.05 ETH should only buy `1.05/1.10 ≈ 0.9545 wrsETH`. The attacker receives ~0.0455 wrsETH in excess.
5. Bot recovers; `updateRate()` is called; L2 oracle updates to 1.10 ETH. Attacker's 1.0 wrsETH is now redeemable for 1.10 ETH — a risk-free profit of ~0.05 ETH extracted from existing holders' accrued yield.
6. The attack scales linearly with deposit size and is repeatable across every L2 pool deployment (`RSETHPoolV3`, `RSETHPoolNoWrapper`) that uses `CrossChainRateReceiver` as its oracle. [6](#0-5) [7](#0-6) [8](#0-7)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-105)
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
    }

    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L231-244)
```text
    function deposit(string memory referralId) external payable nonReentrant whenNotPaused {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        rsETH.safeTransfer(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L277-286)
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

**File:** contracts/cross-chain/MultiChainRateProvider.sol (L108-137)
```text
    function updateRate() external payable nonReentrant {
        uint256 latestRate = getLatestRate();

        rate = latestRate;

        lastUpdated = block.timestamp;

        bytes memory _payload = abi.encode(latestRate);

        uint256 rateReceiversLength = rateReceivers.length;

        for (uint256 i; i < rateReceiversLength;) {
            uint16 dstChainId = uint16(rateReceivers[i]._chainId);

            bytes memory remoteAndLocalAddresses = abi.encodePacked(rateReceivers[i]._contract, address(this));

            (uint256 estimatedFee,) = ILayerZeroEndpoint(layerZeroEndpoint)
                .estimateFees(dstChainId, address(this), _payload, false, bytes(""));

            ILayerZeroEndpoint(layerZeroEndpoint).send{ value: estimatedFee }(
                dstChainId, remoteAndLocalAddresses, _payload, payable(msg.sender), address(0x0), bytes("")
            );

            unchecked {
                ++i;
            }
        }

        emit RateUpdated(rate);
    }
```
