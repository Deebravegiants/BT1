### Title
stETH Transfer Shortfall Causes rsETH Over-Minting in `LRTDepositPool.depositAsset()` - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositAsset()` computes the rsETH amount to mint from the caller-supplied `depositAmount` **before** the `safeTransferFrom` call. Because stETH is a rebasing token that delivers 1–2 wei less than the requested transfer amount, the pool mints rsETH against a nominal deposit that is larger than the actual balance received, creating a persistent, accumulating undercollateralization.

### Finding Description
In `LRTDepositPool.depositAsset()`, `_beforeDeposit` is called first to compute `rsethAmountToMint` from the user-supplied `depositAmount`. The actual token transfer happens afterward:

```solidity
// contracts/LRTDepositPool.sol  lines 110-117
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);
``` [1](#0-0) 

`_beforeDeposit` delegates the mint calculation to `getRsETHAmountToMint(asset, depositAmount)`:

```solidity
// contracts/LRTDepositPool.sol  lines 665-665
rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
``` [2](#0-1) 

stETH is explicitly integrated into the protocol — the contract imports `ILido` and exposes `stakeEthForStETH`, confirming stETH is a first-class supported asset: [3](#0-2) [4](#0-3) 

When a user deposits stETH, `safeTransferFrom` delivers `depositAmount − 1` or `depositAmount − 2` wei to the pool due to stETH's internal share-rounding. The pool, however, mints rsETH calculated from the full `depositAmount`. The result is that the pool holds fewer stETH than the rsETH it has issued accounts for.

### Impact Explanation
Every stETH deposit mints 1–2 wei worth of rsETH in excess of the actual assets received. This shortfall accumulates across all stETH deposits, causing the protocol to be persistently undercollateralized. Existing rsETH holders bear the dilution: the rsETH price (backed by real assets) is fractionally lower than it should be after each stETH deposit. This matches the **"contract fails to deliver promised returns"** impact class — **Low severity**.

### Likelihood Explanation
stETH is a core supported asset on L1. Every unprivileged user who calls `depositAsset` with stETH triggers the shortfall. No special conditions or attacker coordination are required. **Likelihood: Medium.**

### Recommendation
Measure the actual balance delta after the transfer and use that for minting:

```solidity
function depositAsset(
    address asset,
    uint256 depositAmount,
    uint256 minRSETHAmountExpected,
    string calldata referralId
) external nonReentrant whenNotPaused onlySupportedERC20Token(asset) {
+   uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
    IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
+   uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

-   uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);
+   uint256 rsethAmountToMint = _beforeDeposit(asset, actualReceived, minRSETHAmountExpected);

    _mintRsETH(rsethAmountToMint);
    emit AssetDeposit(msg.sender, asset, actualReceived, rsethAmountToMint, referralId);
}
```

### Proof of Concept
1. Alice calls `LRTDepositPool.depositAsset(stETH, 1e18, 0, "")`.
2. `_beforeDeposit` computes `rsethAmountToMint` from `1e18` stETH at the current oracle price — e.g., `~0.9997e18` rsETH.
3. `safeTransferFrom` executes; due to stETH share rounding, the pool receives `1e18 − 1` wei of stETH.
4. `_mintRsETH(~0.9997e18)` mints rsETH calculated from `1e18`, not `1e18 − 1`.
5. The pool is now short 1 wei of stETH relative to the rsETH it has issued.
6. Repeated across thousands of deposits, the shortfall grows, fractionally diluting all rsETH holders.

### Citations

**File:** contracts/LRTDepositPool.sol (L22-22)
```text
import { ILido } from "./external/lido/ILido.sol";
```

**File:** contracts/LRTDepositPool.sol (L110-117)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
```

**File:** contracts/LRTDepositPool.sol (L565-571)
```text
    function stakeEthForStETH(address referral, uint256 ethAmount) external onlyLRTManager {
        address stETHAddress = lrtConfig.getLSTToken(LRTConstants.ST_ETH_TOKEN);

        uint256 stETHShares = ILido(stETHAddress).submit{ value: ethAmount }(referral);

        emit AssetStaked(stETHAddress, ethAmount, stETHShares);
    }
```

**File:** contracts/LRTDepositPool.sol (L648-670)
```text
    function _beforeDeposit(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected
    )
        private
        view
        returns (uint256 rsethAmountToMint)
    {
        if (depositAmount == 0 || depositAmount < minAmountToDeposit) {
            revert InvalidAmountToDeposit();
        }

        if (_checkIfDepositAmountExceedesCurrentLimit(asset, depositAmount)) {
            revert MaximumDepositLimitReached();
        }

        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);

        if (rsethAmountToMint < minRSETHAmountExpected) {
            revert MinimumAmountToReceiveNotMet();
        }
    }
```
