### Title
Accounting Underflow in `transferAssetToDepositPool` Zeros `ethValueInWithdrawal` While LSTs Remain in Converter, Enabling Cheap rsETH Minting — (`contracts/LRTConverter.sol`)

---

### Summary

The floor-to-zero arithmetic in `transferAssetToDepositPool` can set `ethValueInWithdrawal` to `0` while LST tokens (e.g. stETH) still physically reside in the converter. Because the converter's LST holdings are **exclusively** tracked through `ethValueInWithdrawal` in the TVL calculation, the remaining tokens become invisible to the protocol. A public call to `updateRSETHPrice()` then bakes the deflated TVL into the stored rsETH price, allowing any depositor to mint rsETH at below-fair-value and profit when the true value is later recognized.

---

### Finding Description

**Root cause — `LRTConverter.sol` line 163:**

```solidity
ethValueInWithdrawal = ethValueInWithdrawal > assetValue ? ethValueInWithdrawal - assetValue : 0;
```

`ethValueInWithdrawal` is credited at the oracle price at the time of *deposit into the converter* and debited at the oracle price at the time of *return to the deposit pool*. If the oracle price rises between the two operations, the debit for a partial return can exceed the entire accumulated credit, flooring the variable to zero even though other LST batches remain in the converter. [1](#0-0) 

**Why the remaining tokens become invisible:**

`getAssetDistributionData` explicitly sets `assetLyingInConverter = 0` for every LST, delegating converter accounting entirely to `getETHDistributionData`, which reads only `ethValueInWithdrawal`. [2](#0-1) [3](#0-2) 

**Why the deflated price is exploitable:**

`updateRSETHPrice()` is **public** — any caller can trigger it when the protocol is not paused. [4](#0-3) 

`_getTotalEthInProtocol` calls `getTotalAssetDeposits` for every supported asset, which for ETH routes through `getETHDistributionData` → `ethValueInWithdrawal`. A zeroed `ethValueInWithdrawal` directly reduces `totalETHInProtocol` and therefore `newRsETHPrice`. [5](#0-4) 

`getRsETHAmountToMint` divides by the stored `rsETHPrice`, so a deflated price mints more rsETH per unit deposited. [6](#0-5) 

---

### Impact Explanation

**High — Theft of unclaimed yield.**

When `ethValueInWithdrawal` is zeroed while batch B of stETH remains in the converter:

- The TVL is understated by `B * P2 / 1e18`.
- `rsETHPrice` is deflated proportionally.
- An attacker deposits at the deflated price and receives excess rsETH.
- When batch B is eventually returned via `transferAssetToDepositPool`, TVL is restored, rsETH price rises, and the attacker redeems at a profit — extracting value from existing rsETH holders (their share of the yield accrued by the converter's LST holdings).

---

### Likelihood Explanation

The triggering condition is `A * P2 >= (A + B) * P1`, i.e. a price increase of at least `B/A * 100%`. This is easily reached in practice:

- If the operator moves a large batch A first and a small residual batch B second (common operational pattern), even a 1–2% stETH price appreciation (routine staking yield) satisfies the condition.
- The operator is performing entirely legitimate operations; no compromise or collusion is required.
- `updateRSETHPrice()` is permissionless, so the attacker can atomically trigger the price update and deposit in the same block.

---

### Recommendation

Replace the floor-to-zero subtraction with a price-neutral debit that tracks **token amounts** rather than ETH values, or maintain a separate per-asset token balance in the converter and compute the ETH value live from the current oracle price:

```solidity
// Instead of storing ETH value, store token amounts per asset
mapping(address => uint256) public assetAmountInWithdrawal;

// On deposit into converter:
assetAmountInWithdrawal[_asset] += _amount;

// On return to deposit pool:
assetAmountInWithdrawal[_asset] -= _amount; // reverts on underflow

// ethValueInWithdrawal (view):
function ethValueInWithdrawal() external view returns (uint256 total) {
    for each asset: total += assetAmountInWithdrawal[asset] * oracle.getAssetPrice(asset) / 1e18;
}
```

This ensures the reported ETH value always reflects the actual tokens held, regardless of price movements between deposit and return.

---

### Proof of Concept

```solidity
// Setup:
// A = 100e18 stETH, B = 10e18 stETH, P1 = 1.00e18, P2 = 1.12e18

// Step 1: operator moves two batches to converter at P1
transferAssetFromDepositPool(stETH, 100e18);  // ethValueInWithdrawal = 100e18
transferAssetFromDepositPool(stETH,  10e18);  // ethValueInWithdrawal = 110e18

// Step 2: stETH oracle price rises to 1.12e18 (12% appreciation)

// Step 3: operator returns first batch at P2
// assetValue = 100e18 * 1.12e18 / 1e18 = 112e18 > 110e18
transferAssetToDepositPool(stETH, 100e18);    // ethValueInWithdrawal = 0  ← BUG
// 10e18 stETH (worth 11.2 ETH) still in converter, completely untracked

// Step 4: attacker calls updateRSETHPrice()
// totalETHInProtocol is understated by 11.2 ETH
// rsETHPrice is deflated

// Step 5: attacker deposits ETH, receives excess rsETH at deflated price

// Step 6: operator returns second batch
transferAssetToDepositPool(stETH, 10e18);     // TVL restored

// Step 7: attacker calls updateRSETHPrice() again, rsETHPrice rises
// Attacker redeems rsETH at profit — yield stolen from existing holders

// Assert (should hold but doesn't after step 3):
assert(ethValueInWithdrawal >= 10e18 * 1.12e18 / 1e18);  // FAILS: 0 >= 11.2e18
```

### Citations

**File:** contracts/LRTConverter.sol (L140-163)
```text
        ethValueInWithdrawal += (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        IERC20(_asset).safeTransferFrom(lrtDepositPoolAddress, address(this), _amount);
    }

    /// @notice send asset from LRTConverter to deposit pool
    /// @dev Only callable by Asset Transfer Role and asset needs to be approved
    /// @param _asset Asset address to send
    /// @param _amount Asset amount to send
    function transferAssetToDepositPool(
        address _asset,
        uint256 _amount
    )
        external
        onlySupportedERC20Token(_asset)
        onlyAssetTransferRole
    {
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address lrtOracleAddress = lrtConfig.getContract(LRTConstants.LRT_ORACLE);
        ILRTOracle lrtOracle = ILRTOracle(lrtOracleAddress);
        uint256 assetValue = (_amount * lrtOracle.getAssetPrice(_asset)) / 1e18;

        // Set to 0 if assetValue exceeds ethValueInWithdrawal, otherwise subtract assetValue
        ethValueInWithdrawal = ethValueInWithdrawal > assetValue ? ethValueInWithdrawal - assetValue : 0;
```

**File:** contracts/LRTDepositPool.sol (L460-460)
```text
        assetLyingInConverter = 0; // assets in converter are accounted in their eth value => getETHDistributionData()
```

**File:** contracts/LRTDepositPool.sol (L498-499)
```text
        address lrtConverter = lrtConfig.getContract(LRTConstants.LRT_CONVERTER);
        ethLyingInConverter = ILRTConverter(lrtConverter).ethValueInWithdrawal();
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTOracle.sol (L87-89)
```text
    function updateRSETHPrice() public whenNotPaused {
        _updateRsETHPrice();
    }
```

**File:** contracts/LRTOracle.sol (L331-349)
```text
    function _getTotalEthInProtocol() private view returns (uint256 totalETHInProtocol) {
        address lrtDepositPoolAddr = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);
        address[] memory supportedAssets = lrtConfig.getSupportedAssetList();
        uint256 supportedAssetCount = supportedAssets.length;

        for (uint16 assetIdx; assetIdx < supportedAssetCount;) {
            address asset = supportedAssets[assetIdx];
            // assetER is in 1e18 precision (1.0 = 1e18)
            uint256 assetER = getAssetPrice(asset);
            // totalAssetAmt is in 1e18 precision (standard token decimals)
            uint256 totalAssetAmt = ILRTDepositPool(lrtDepositPoolAddr).getTotalAssetDeposits(asset);

            totalETHInProtocol += totalAssetAmt.mulWad(assetER);

            unchecked {
                ++assetIdx;
            }
        }
    }
```
