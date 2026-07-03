### Title
Fee-on-Transfer Token Deposits Cause rsETH Over-Minting and Protocol Insolvency - (File: contracts/LRTDepositPool.sol)

### Summary

`LRTDepositPool::depositAsset` calculates the rsETH mint amount from the caller-supplied `depositAmount` parameter **before** the actual `safeTransferFrom` executes. If a supported asset has a transfer fee, the contract receives fewer tokens than `depositAmount`, but mints rsETH for the full nominal amount, inflating rsETH supply relative to actual protocol assets.

### Finding Description

In `depositAsset`, the rsETH mint amount is computed in `_beforeDeposit` using the raw `depositAmount` argument: [1](#0-0) 

`_beforeDeposit` calls `getRsETHAmountToMint(asset, depositAmount)`: [2](#0-1) 

which computes: [3](#0-2) 

The mint amount is therefore fixed to `depositAmount` before the transfer. The actual transfer then occurs:

```solidity
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);
``` [4](#0-3) 

For a fee-on-transfer token, `safeTransferFrom` delivers `depositAmount - fee` to the contract, but `rsethAmountToMint` was already fixed to the full `depositAmount`. The user receives rsETH backed by more assets than actually exist in the protocol.

The oracle's `_getTotalEthInProtocol` uses `getTotalAssetDeposits`, which reads live `balanceOf` values: [5](#0-4) 

So the oracle correctly sees the lower real balance, but rsETH supply is already inflated — the rsETH price computed by `LRTOracle` drops, diluting all existing holders.

### Impact Explanation

**Critical — Protocol insolvency.** Each deposit with a fee-on-transfer token mints rsETH for `depositAmount` but only `depositAmount * (1 - fee%)` tokens enter the protocol. Over repeated deposits, the rsETH supply grows faster than the backing assets. When `LRTOracle::updateRSETHPrice` recalculates the price using actual `balanceOf` values, the rsETH price is suppressed, socializing the loss across all rsETH holders. At scale this constitutes direct, permanent dilution of all holders' claims.

### Likelihood Explanation

**Low-to-Medium.** The current supported assets (stETH, ETHx) are not fee-on-transfer tokens. However, the protocol is explicitly designed to be extensible — the admin can add any new LST via `LRTConfig`. If a rebasing or fee-bearing LST is ever added (e.g., a token that charges a fee on transfer to fund a DAO), the vulnerability is immediately exploitable by any depositor without any privileged access. The depositor only needs to call the public `depositAsset` function.

### Recommendation

Measure the actual received amount by comparing balances before and after the transfer, and mint rsETH based on the received amount rather than the nominal parameter:

```solidity
function depositAsset(...) external ... {
    uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
    IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
    uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

    uint256 rsethAmountToMint = _beforeDeposit(asset, actualReceived, minRSETHAmountExpected);
    _mintRsETH(rsethAmountToMint);
    ...
}
```

Alternatively, explicitly document and enforce that only non-fee-bearing tokens may be added as supported assets, and add a validation check in the asset-addition path.

### Proof of Concept

1. Admin adds a fee-on-transfer LST (1% fee) as a supported asset.
2. Attacker calls `depositAsset(feeToken, 100e18, 0, "")`.
3. `_beforeDeposit` computes `rsethAmountToMint` for `100e18` tokens at current oracle price.
4. `safeTransferFrom` delivers only `99e18` tokens to `LRTDepositPool`.
5. `_mintRsETH` mints rsETH for `100e18` worth of assets.
6. `LRTOracle::updateRSETHPrice` reads `getTotalAssetDeposits` → `balanceOf` → `99e18`.
7. rsETH price = `(99e18 * assetPrice) / rsethSupply` — lower than before, diluting all holders.
8. Repeated deposits amplify the insolvency proportionally to the fee rate and deposit volume. [6](#0-5) [7](#0-6)

### Citations

**File:** contracts/LRTDepositPool.sol (L99-118)
```text
    function depositAsset(
        address asset,
        uint256 depositAmount,
        uint256 minRSETHAmountExpected,
        string calldata referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedERC20Token(asset)
    {
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
    }
```

**File:** contracts/LRTDepositPool.sol (L444-448)
```text
        assetLyingInDepositPool = IERC20(asset).balanceOf(address(this));

        uint256 ndcsCount = nodeDelegatorQueue.length;
        for (uint256 i; i < ndcsCount;) {
            assetLyingInNDCs += IERC20(asset).balanceOf(nodeDelegatorQueue[i]);
```

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L665-665)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```

**File:** contracts/LRTOracle.sol (L331-348)
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
```
