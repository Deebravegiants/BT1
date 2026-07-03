### Title
Fee-on-Transfer Token Deposits Mint Excess rsETH, Causing Protocol Insolvency - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositAsset()` calculates the rsETH amount to mint using the caller-supplied `depositAmount` **before** the transfer occurs, then mints that pre-calculated amount regardless of how many tokens were actually received. For fee-on-transfer tokens, the contract receives fewer tokens than `depositAmount`, but mints rsETH as if the full amount arrived — inflating rsETH supply beyond its real backing.

### Finding Description
In `depositAsset()`, `_beforeDeposit()` is called first and computes `rsethAmountToMint` using the raw `depositAmount` parameter: [1](#0-0) 

`_beforeDeposit` delegates to `getRsETHAmountToMint(asset, depositAmount)`: [2](#0-1) 

which computes: [3](#0-2) 

The `safeTransferFrom` call follows: [4](#0-3) 

For a fee-on-transfer token, `address(this)` receives `depositAmount - fee`, but `rsethAmountToMint` was already fixed to the full `depositAmount`. The subsequent `_mintRsETH(rsethAmountToMint)` mints rsETH backed by fewer real assets than accounted for: [5](#0-4) 

The same pattern exists in `RsETHTokenWrapper._deposit()` and `AGETHTokenWrapper._deposit()`, where `_mint(_to, _amount)` is called with the pre-transfer `_amount` rather than the actual received balance delta: [6](#0-5) [7](#0-6) 

### Impact Explanation
Every deposit of a fee-on-transfer asset mints more rsETH than the protocol actually holds in backing. Over time, the cumulative over-minting makes rsETH redeemable for more assets than the protocol possesses, leading to **protocol insolvency**. Later redeemers cannot be made whole. This is a Critical impact.

### Likelihood Explanation
The protocol's `allowedTokens` / `onlySupportedERC20Token` gating means the vulnerability is only triggered if a fee-on-transfer token is added as a supported asset. The current supported assets (stETH, ETHx, etc.) do not charge transfer fees today, but the protocol is designed to be extensible. Any future addition of a fee-on-transfer LST (or a token whose fee is activated later, as with USDT) immediately opens this path to any unprivileged depositor. Likelihood is Medium.

### Recommendation
In `depositAsset()`, measure the actual balance change around the `safeTransferFrom` call and use that delta — not the caller-supplied `depositAmount` — for all subsequent calculations:

```solidity
uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;

uint256 rsethAmountToMint = getRsETHAmountToMint(asset, actualReceived);
if (rsethAmountToMint < minRSETHAmountExpected) revert MinimumAmountToReceiveNotMet();
_mintRsETH(rsethAmountToMint);
```

Apply the same balance-delta pattern in `RsETHTokenWrapper._deposit()` and `AGETHTokenWrapper._deposit()`.

### Proof of Concept
1. Governance adds a fee-on-transfer token `FEE_TOKEN` (1% fee) as a supported asset.
2. Attacker calls `depositAsset(FEE_TOKEN, 1000e18, 0, "")`.
3. `_beforeDeposit` computes `rsethAmountToMint` based on `1000e18`.
4. `safeTransferFrom` transfers `1000e18` from attacker; contract receives `990e18` (1% fee taken).
5. `_mintRsETH` mints rsETH equivalent to `1000e18` of `FEE_TOKEN`.
6. The protocol's rsETH supply is now backed by only `990e18` tokens but represents `1000e18` worth — a 1% insolvency gap per deposit.
7. Repeated deposits compound the gap until the protocol cannot honor all redemptions. [8](#0-7)

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

**File:** contracts/LRTDepositPool.sol (L520-520)
```text
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
```

**File:** contracts/LRTDepositPool.sol (L665-665)
```text
        rsethAmountToMint = getRsETHAmountToMint(asset, depositAmount);
```

**File:** contracts/LRTDepositPool.sol (L686-690)
```text
    function _mintRsETH(uint256 rsethAmountToMint) private {
        address rsethToken = lrtConfig.rsETH();
        // mint rseth for user
        IRSETH(rsethToken).mint(msg.sender, rsethAmountToMint);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L134-141)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L125-132)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, _to, _amount);
    }
```
