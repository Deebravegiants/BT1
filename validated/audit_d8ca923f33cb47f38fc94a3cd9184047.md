### Title
Fee-on-Transfer Token Accounting Gap Causes rsETH Over-Minting and Protocol Insolvency - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositAsset` computes the rsETH minting amount from the caller-supplied `depositAmount` parameter **before** the actual token transfer executes. If a fee-on-transfer LST is ever added to the supported-asset whitelist, the contract mints rsETH against the nominal deposit amount while receiving fewer tokens, inflating the rsETH supply relative to actual TVL and eventually causing insolvency for the last redeemers.

### Finding Description
In `depositAsset` the execution order is:

1. `rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected)` — calls `getRsETHAmountToMint(asset, depositAmount)`, which prices `depositAmount` tokens at the oracle rate and returns the rsETH to mint.
2. `IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount)` — a fee-on-transfer token silently delivers `depositAmount − fee` to the contract; the shortfall is never detected.
3. `_mintRsETH(rsethAmountToMint)` — mints rsETH calculated against the full nominal `depositAmount`, not the actual received amount. [1](#0-0) 

The actual balance received is never measured. `LRTOracle` will eventually reflect the true (lower) asset balance when computing the rsETH/ETH rate, but the rsETH supply is already inflated by the fee amount on every deposit. The rsETH/asset ratio drifts permanently: rsETH holders collectively own more rsETH than the underlying assets can redeem.

The identical pattern exists in `RSETHPoolV3.deposit(address token, uint256 amount, …)`: `safeTransferFrom` is called first, then `viewSwapRsETHAmountAndFee(amount, token)` is called with the original nominal `amount`, and `wrsETH.mint(msg.sender, rsETHAmount)` mints against that nominal figure. [2](#0-1) 

The root cause is that `LRTConfig._addNewSupportedAsset` performs no on-chain validation that the token being whitelisted is not a fee-on-transfer token. [3](#0-2) 

### Impact Explanation
**Critical — Protocol insolvency.** Every deposit of a fee-on-transfer token mints excess rsETH. The rsETH supply grows faster than the underlying asset balance. When users redeem rsETH through `LRTUnstakingVault`, the last redeemers cannot be made whole — their rsETH represents assets that do not exist in the protocol. This is a permanent, compounding loss of funds for rsETH holders proportional to the token's transfer fee and total deposit volume.

### Likelihood Explanation
**Low.** The vulnerability is latent: it activates only if `TIME_LOCK_ROLE` adds a fee-on-transfer token to `LRTConfig.supportedAssetList` via `addNewSupportedAsset`. The protocol has no on-chain guard that rejects fee-on-transfer tokens during asset whitelisting. Given the protocol's stated intent to support multiple LSTs and the complete absence of any fee-on-transfer check in `_addNewSupportedAsset`, a governance mistake or a future LST that introduces a transfer fee would silently trigger this path with no warning. [4](#0-3) 

### Recommendation
In `depositAsset`, measure the actual received amount by snapshotting the contract balance before and after `safeTransferFrom`, and use the delta as the input to `getRsETHAmountToMint`:

```solidity
uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;
uint256 rsethAmountToMint = _beforeDeposit(asset, actualReceived, minRSETHAmountExpected);
_mintRsETH(rsethAmountToMint);
```

Apply the same fix to `RSETHPoolV3.deposit`. Additionally, add a fee-on-transfer detection check inside `LRTConfig._addNewSupportedAsset` to reject tokens that deliver fewer tokens than the transfer amount.

### Proof of Concept
1. Governance adds a fee-on-transfer LST (e.g., 1 % fee) to `LRTConfig` via `addNewSupportedAsset` — no on-chain check prevents this.
2. Alice calls `LRTDepositPool.depositAsset(feeToken, 100e18, 0, "")`.
3. `_beforeDeposit` computes `rsethAmountToMint` based on `100e18` tokens at the oracle price.
4. `safeTransferFrom` delivers `99e18` tokens to the contract (1 % fee taken by the token).
5. `_mintRsETH` mints rsETH based on `100e18` — 1 % more than the actual value received.
6. Repeated deposits inflate the rsETH supply relative to actual TVL.
7. `LRTOracle` eventually prices rsETH lower (reflecting the true asset balance), but the excess rsETH already minted cannot be recalled.
8. The last rsETH redeemers find insufficient underlying assets to cover their redemption — permanent loss of funds.

### Citations

**File:** contracts/LRTDepositPool.sol (L110-117)
```text
        // checks
        uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

        // interactions
        IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
        _mintRsETH(rsethAmountToMint);

        emit AssetDeposit(msg.sender, asset, depositAmount, rsethAmountToMint, referralId);
```

**File:** contracts/pools/RSETHPoolV3.sol (L284-292)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
```

**File:** contracts/LRTConfig.sol (L99-101)
```text
    function addNewSupportedAsset(address asset, uint256 depositLimit) external onlyRole(LRTConstants.TIME_LOCK_ROLE) {
        _addNewSupportedAsset(asset, depositLimit);
    }
```

**File:** contracts/LRTConfig.sol (L106-118)
```text
    function _addNewSupportedAsset(address asset, uint256 depositLimit) private {
        UtilLib.checkNonZeroAddress(asset);
        if (depositLimit == 0) {
            revert InvalidDepositLimit();
        }
        if (isSupportedAsset[asset]) {
            revert AssetAlreadySupported();
        }
        isSupportedAsset[asset] = true;
        supportedAssetList.push(asset);
        depositLimitByAsset[asset] = depositLimit;
        emit AddedNewSupportedAsset(asset, depositLimit);
    }
```
