### Title
No Staleness Check on `CrossChainRateReceiver.getRate()` Allows Depositors to Mint Excess rsETH at Stale Rate — (File: contracts/cross-chain/CrossChainRateReceiver.sol)

---

### Summary

The `CrossChainRateReceiver` contract stores a `rate` and a `lastUpdated` timestamp, but `getRate()` returns `rate` unconditionally with no staleness guard. All L2 pool contracts use this oracle to price rsETH minting. When the true L1 rsETH/ETH rate rises (yield accrual) but the L2 oracle is not refreshed, any depositor can exploit the stale (lower) rate to receive more rsETH than they are entitled to, extracting value from existing rsETH holders.

---

### Finding Description

`CrossChainRateReceiver.getRate()` simply returns the stored `rate`:

```solidity
// contracts/cross-chain/CrossChainRateReceiver.sol:103-105
function getRate() external view returns (uint256) {
    return rate;
}
```

The `lastUpdated` field is written on every `lzReceive` call but is **never read** inside `getRate()`. [1](#0-0) 

Every L2 pool contract (`RSETHPool`, `RSETHPoolV3`, `RSETHPoolNoWrapper`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) calls `IOracle(rsETHOracle).getRate()` to compute the rsETH minting amount:

```solidity
// contracts/pools/RSETHPoolV3.sol:235-237
function getRate() public view returns (uint256) {
    return IOracle(rsETHOracle).getRate();
}
``` [2](#0-1) 

The minting formula divides by this rate:

```solidity
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
``` [3](#0-2) 

The rate is pushed from L1 via `RSETHMultiChainRateProvider.updateRate()`, which reads `ILRTOracle(rsETHPriceOracle).rsETHPrice()` and sends it over LayerZero. [4](#0-3) 

`updateRate()` is permissionless but requires the caller to supply ETH to cover LayerZero messaging fees. [5](#0-4) 

There is no on-chain incentive or enforcement mechanism that guarantees timely rate updates. As rsETH accrues staking yield on L1, `LRTOracle.rsETHPrice` rises, but the L2 receiver's `rate` remains frozen at the last pushed value until someone voluntarily pays to refresh it. [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

A depositor who deposits on L2 while the oracle is stale receives `amountAfterFee * 1e18 / staleRate` rsETH. Because `staleRate < trueRate`, the depositor receives more rsETH than the ETH they contributed is worth at the current true exchange rate. When they later redeem on L1 at the true (higher) rate, they extract ETH that belongs to existing rsETH holders. The magnitude scales with (a) how long the rate has been stale and (b) the deposit size. [7](#0-6) 

---

### Likelihood Explanation

**Medium.** The `updateRate()` call requires the caller to pay LayerZero fees in ETH with no reimbursement mechanism. During periods of high gas costs or low protocol activity, the rate will naturally drift stale. An attacker can passively monitor the divergence between the on-chain L1 `rsETHPrice` and the L2 receiver's `rate`, then deposit precisely when the gap is largest. No privileged access is required. [8](#0-7) 

---

### Recommendation

Add a configurable `MAX_STALENESS` constant and revert in `getRate()` if the rate is too old:

```solidity
uint256 public constant MAX_STALENESS = 24 hours;

function getRate() external view returns (uint256) {
    require(block.timestamp - lastUpdated <= MAX_STALENESS, "Rate is stale");
    return rate;
}
```

This converts a silent mis-pricing into a hard revert, preventing deposits when the oracle has not been refreshed. Pair this with an on-chain keeper incentive (e.g., a small ETH reward funded from protocol fees) to ensure timely updates. [9](#0-8) 

---

### Proof of Concept

1. At time T₀, `LRTOracle.rsETHPrice = 1.05e18` and the L2 `CrossChainRateReceiver.rate = 1.05e18`.
2. rsETH accrues yield; at time T₁, `LRTOracle.rsETHPrice = 1.10e18`. No one calls `updateRate()` (LayerZero fees are non-trivial).
3. L2 `CrossChainRateReceiver.rate` remains `1.05e18`.
4. Attacker calls `RSETHPoolV3.deposit{value: 10 ether}("")`:
   - `rsETHAmount = 10e18 * 1e18 / 1.05e18 ≈ 9.524e18` rsETH minted.
   - Correct amount at true rate: `10e18 * 1e18 / 1.10e18 ≈ 9.091e18` rsETH.
   - Excess: `≈ 0.433e18` rsETH.
5. Attacker bridges rsETH to L1 and redeems at `1.10e18` rate, receiving `≈ 10.476 ETH` for a `10 ETH` deposit.
6. Profit: `≈ 0.476 ETH` extracted from existing rsETH holders per 10 ETH deposited. [10](#0-9) [11](#0-10)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L13-17)
```text
    uint256 public rate;

    /// @notice Last time rate was updated
    uint256 public lastUpdated;

```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-100)
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
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L102-105)
```text
    /// @notice Gets the last stored rate in the contract
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L234-237)
```text
    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
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

**File:** contracts/pools/RSETHPoolNoWrapper.sol (L211-222)
```text
        _grantRole(BRIDGER_ROLE, manager);

        rsETH = IERC20(_rsETH);
        feeBps = _feeBps;
        rsETHOracle = _rsETHOracle;
        isEthDepositEnabled = _isEthDepositEnabled;
    }

    /// @dev Gets the rate from the rsETHOracle
    function getRate() public view returns (uint256) {
        return IOracle(rsETHOracle).getRate();
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
