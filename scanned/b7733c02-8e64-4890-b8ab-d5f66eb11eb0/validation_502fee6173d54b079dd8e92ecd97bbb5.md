### Title
Immutable oracle address in `RSETHRateProvider` / `RSETHMultiChainRateProvider` not updated when `LRTConfig` replaces the oracle - (File: contracts/cross-chain/RSETHRateProvider.sol, contracts/cross-chain/RSETHMultiChainRateProvider.sol)

---

### Summary
`RSETHRateProvider` and `RSETHMultiChainRateProvider` permanently cache the `LRTOracle` address as an `immutable` variable at construction time. `LRTConfig` exposes `setContract()` which allows the admin to replace the canonical oracle address at any time. After such a replacement, the rate providers continue to read from the old, potentially stale or decommissioned oracle, while every other L1 protocol component (deposit pool, withdrawal manager, etc.) immediately uses the new one. This is the exact state-desync pattern described in M-01.

---

### Finding Description

`RSETHRateProvider` stores the oracle address as `immutable`:

```solidity
// contracts/cross-chain/RSETHRateProvider.sol
address public immutable rsETHPriceOracle;          // line 11

constructor(address _rsETHPriceOracle, ...) {
    rsETHPriceOracle = _rsETHPriceOracle;           // line 14
    ...
}

function getLatestRate() public view override returns (uint256) {
    return ILRTOracle(rsETHPriceOracle).rsETHPrice(); // line 28
}
```

`RSETHMultiChainRateProvider` has the identical pattern:

```solidity
// contracts/cross-chain/RSETHMultiChainRateProvider.sol
address public immutable rsETHPriceOracle;          // line 10

constructor(address _rsETHPriceOracle, ...) {
    rsETHPriceOracle = _rsETHPriceOracle;           // line 13
}
```

Meanwhile, `LRTConfig` allows the admin to replace the canonical oracle at any time:

```solidity
// contracts/LRTConfig.sol
function setContract(bytes32 contractKey, address contractAddress)
    external onlyRole(DEFAULT_ADMIN_ROLE) {          // line 237
    _setContract(contractKey, contractAddress);
}
```

After `setContract(LRT_ORACLE, newOracleAddress)` is called, every L1 component that calls `lrtConfig.getContract(LRTConstants.LRT_ORACLE)` dynamically receives the new oracle. The rate providers, however, are permanently bound to the old oracle address and have no setter to correct this. There is no mechanism in the protocol to update `rsETHPriceOracle` short of redeploying the rate provider contracts entirely.

---

### Impact Explanation

The rate providers are the sole source of the rsETH/ETH exchange rate propagated cross-chain via LayerZero. L2 pools (`RSETHPoolV3`, `RSETHPoolV3ExternalBridge`, `RSETHPoolV3WithNativeChainBridge`) call `IOracle(rsETHOracle).getRate()` on every deposit to determine how many `wrsETH` tokens to mint:

```solidity
// contracts/pools/RSETHPoolV3.sol
rsETHAmount = amountAfterFee * 1e18 / rsETHToETHrate;  // line 307
```

If the stale oracle reports a rate lower than the true current rate, depositors receive more `wrsETH` than the ETH they contributed is worth, draining the protocol's backing. If it reports a higher rate, depositors are shortchanged. Either direction constitutes a failure to deliver promised returns; the downward-rate case escalates to protocol insolvency.

**Impact: Low (contract fails to deliver promised returns) escalating to Critical (protocol insolvency) depending on the direction of the stale rate.**

---

### Likelihood Explanation

The oracle is replaced only by the `DEFAULT_ADMIN_ROLE`, which is a privileged but realistic operational event (oracle upgrade, migration to a new price model, emergency replacement after a bug). The protocol already has `setContract` wired for exactly this purpose. When it is exercised, the desync is silent — no revert, no event from the rate provider — making it easy to miss that the cross-chain rate is now sourced from a decommissioned contract.

**Likelihood: Low-Medium** — requires an admin oracle rotation, which is a planned operational action, not an exotic edge case.

---

### Recommendation

Replace the `immutable` cache with a dynamic lookup through `LRTConfig`, mirroring the pattern used by every other L1 component:

```solidity
// Instead of:
address public immutable rsETHPriceOracle;

// Use:
ILRTConfig public lrtConfig;

function getLatestRate() public view override returns (uint256) {
    address oracle = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
    return ILRTOracle(oracle).rsETHPrice();
}
```

Alternatively, expose a privileged setter so the rate provider can be updated in the same governance transaction that calls `LRTConfig.setContract`.

---

### Proof of Concept

1. `RSETHRateProvider` is deployed with `LRTOracle_v1` as `rsETHPriceOracle`.
2. Admin calls `LRTConfig.setContract(LRT_ORACLE, LRTOracle_v2)`. All L1 components now use `LRTOracle_v2`.
3. `RSETHRateProvider.getLatestRate()` still calls `LRTOracle_v1.rsETHPrice()`.
4. If `LRTOracle_v1` was replaced because it was returning a depressed price (e.g., due to a bug), the rate provider continues to broadcast that depressed rate to every L2 chain via LayerZero.
5. L2 pools receive the stale low rate and mint excess `wrsETH` for every depositor until the rate provider is redeployed — a window that could span hours or days. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** contracts/cross-chain/RSETHRateProvider.sol (L11-14)
```text
    address public immutable rsETHPriceOracle;

    constructor(address _rsETHPriceOracle, uint16 _dstChainId, address _layerZeroEndpoint) {
        rsETHPriceOracle = _rsETHPriceOracle;
```

**File:** contracts/cross-chain/RSETHRateProvider.sol (L27-29)
```text
    function getLatestRate() public view override returns (uint256) {
        return ILRTOracle(rsETHPriceOracle).rsETHPrice();
    }
```

**File:** contracts/cross-chain/RSETHMultiChainRateProvider.sol (L10-13)
```text
    address public immutable rsETHPriceOracle;

    constructor(address _rsETHPriceOracle, address _layerZeroEndpoint) {
        rsETHPriceOracle = _rsETHPriceOracle;
```

**File:** contracts/LRTConfig.sol (L237-250)
```text
    function setContract(bytes32 contractKey, address contractAddress) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _setContract(contractKey, contractAddress);
    }

    /// @dev private function to set a contract
    /// @param key Contract key
    /// @param val Contract address
    function _setContract(bytes32 key, address val) private {
        UtilLib.checkNonZeroAddress(val);
        if (contractMap[key] == val) {
            revert ValueAlreadyInUse();
        }
        contractMap[key] = val;
        emit SetContract(key, val);
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
