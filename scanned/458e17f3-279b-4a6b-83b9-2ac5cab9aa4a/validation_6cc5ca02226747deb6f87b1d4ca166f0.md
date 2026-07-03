### Title
Missing Zero-Address Check in `CrossChainRateReceiver` Setter Functions Permanently Freezes Oracle Rate - (File: contracts/cross-chain/CrossChainRateReceiver.sol)

### Summary
`CrossChainRateReceiver.updateLayerZeroEndpoint` and `updateRateProvider` accept `address(0)` without reverting. If either critical address is set to zero, the `lzReceive` function becomes permanently inoperable, freezing the oracle rate used by all L2 deposit pools. Users depositing ETH or LSTs into pools such as `RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, and `RSETHPoolNoWrapper` will receive wrsETH amounts calculated from a permanently stale rate, causing yield mis-accounting.

### Finding Description
`CrossChainRateReceiver` is the on-chain oracle that L2 pools query via `getRate()` to price deposits. Its rate is updated exclusively through `lzReceive`, which is gated by two address checks:

```solidity
// CrossChainRateReceiver.sol L83-91
require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");
...
require(srcAddress == rateProvider, "Src address must be provider");
```

Both `layerZeroEndpoint` and `rateProvider` are set via owner-only setters that perform no zero-address validation:

```solidity
// L54-57
function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
    layerZeroEndpoint = _layerZeroEndpoint;
    ...
}

// L63-66
function updateRateProvider(address _rateProvider) external onlyOwner {
    rateProvider = _rateProvider;
    ...
}
```

If either is set to `address(0)`:
- `msg.sender == address(0)` is impossible in EVM, so `lzReceive` always reverts on the first `require`.
- `srcAddress == address(0)` is impossible for a real LayerZero message, so `lzReceive` always reverts on the second `require`.

In both cases, `rate` is permanently frozen at its last stored value. `getRate()` silently returns the stale rate with no error.

The L2 pools call `getRate()` directly during every deposit:

```solidity
// RSETHPoolV3.sol L304-307
uint256 rsETHToETHrate = getRate();
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```

Because rsETH is a yield-bearing token whose exchange rate increases over time, a frozen (lower) rate causes the pool to mint **more** wrsETH per ETH deposited than the true rate warrants, diluting existing wrsETH holders and siphoning unclaimed yield.

### Impact Explanation
The oracle rate is permanently frozen. Every subsequent user deposit mints wrsETH at an incorrect (stale) rate. As rsETH appreciates, the divergence grows, causing continuous over-minting that dilutes existing holders and constitutes ongoing theft of unclaimed yield. The pool cannot self-correct; only the owner re-setting the address restores liveness.

**Impact: Medium — Permanent freezing of unclaimed yield / ongoing yield theft from existing wrsETH holders.**

### Likelihood Explanation
The owner must call `updateLayerZeroEndpoint(address(0))` or `updateRateProvider(address(0))` — an accidental misconfiguration with no on-chain guard. The absence of a sanity check makes this a realistic operational error during contract upgrades or address rotations. Once set, the damage is silent (no revert on `getRate()`), so it may go undetected for an extended period.

### Recommendation
Add a zero-address guard in both setters, mirroring the pattern used elsewhere in the codebase (e.g., `UtilLib.checkNonZeroAddress`):

```solidity
function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
    require(_layerZeroEndpoint != address(0), "Zero address");
    layerZeroEndpoint = _layerZeroEndpoint;
    emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
}

function updateRateProvider(address _rateProvider) external onlyOwner {
    require(_rateProvider != address(0), "Zero address");
    rateProvider = _rateProvider;
    emit RateProviderUpdated(_rateProvider);
}
```

### Proof of Concept

1. Owner calls `CrossChainRateReceiver.updateLayerZeroEndpoint(address(0))` — no revert, `layerZeroEndpoint` is now `address(0)`.
2. LayerZero delivers a rate update; `lzReceive` is called with `msg.sender = <LZ endpoint>`. The check `require(msg.sender == layerZeroEndpoint)` → `require(<LZ endpoint> == address(0))` reverts. Rate is never updated.
3. rsETH appreciates on L1; the true rate rises from e.g. 1.05e18 to 1.10e18, but `CrossChainRateReceiver.rate` remains at 1.05e18.
4. User calls `RSETHPoolV3.deposit{value: 1 ether}("")`. Pool computes `rsETHAmount = 1e18 * 1e18 / 1.05e18 ≈ 0.952e18` wrsETH instead of the correct `≈ 0.909e18`. User receives ~4.7% excess wrsETH, diluting all existing holders.
5. This over-minting continues indefinitely for every subsequent depositor until the owner notices and corrects the address.

**Root cause:** [1](#0-0) 

**Missing check allows zero address:** [2](#0-1) 

**Downstream gate that becomes permanently blocked:** [3](#0-2) 

**Stale rate silently returned to pool:** [4](#0-3) 

**Pool consumes stale rate for every user deposit:** [5](#0-4)

### Citations

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L54-57)
```text
    function updateLayerZeroEndpoint(address _layerZeroEndpoint) external onlyOwner {
        layerZeroEndpoint = _layerZeroEndpoint;

        emit LayerZeroEndpointUpdated(_layerZeroEndpoint);
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L63-67)
```text
    function updateRateProvider(address _rateProvider) external onlyOwner {
        rateProvider = _rateProvider;

        emit RateProviderUpdated(_rateProvider);
    }
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L82-91)
```text
    function lzReceive(uint16 _srcChainId, bytes memory _srcAddress, uint64, bytes calldata _payload) external {
        require(msg.sender == layerZeroEndpoint, "Sender should be lz endpoint");

        address srcAddress;
        assembly {
            srcAddress := mload(add(_srcAddress, 20))
        }

        require(_srcChainId == srcChainId, "Src chainId must be correct");
        require(srcAddress == rateProvider, "Src address must be provider");
```

**File:** contracts/cross-chain/CrossChainRateReceiver.sol (L103-105)
```text
    function getRate() external view returns (uint256) {
        return rate;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L304-307)
```text
        uint256 rsETHToETHrate = getRate();

        // Calculate the final rsETH amount
        rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;
```
