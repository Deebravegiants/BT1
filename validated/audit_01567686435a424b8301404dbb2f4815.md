### Title
Fee-on-Transfer Token Deposit Mints rsETH Against Unverified Received Amount, Causing Protocol Insolvency - (File: contracts/LRTDepositPool.sol)

### Summary
`LRTDepositPool.depositAsset()` computes the rsETH mint amount from the caller-supplied `depositAmount` parameter **before** executing the token transfer, and never verifies the actual balance change. If a fee-on-transfer ERC20 is ever added as a supported asset, the protocol receives fewer tokens than `depositAmount` but mints rsETH as if it received the full amount — an exact structural analog to M-06's unverified `mintCountTo` outcome.

### Finding Description
In `LRTDepositPool.depositAsset()`, the rsETH mint quantity is fixed by `_beforeDeposit(asset, depositAmount, ...)` using the user-supplied `depositAmount` before the transfer executes:

```solidity
// contracts/LRTDepositPool.sol lines 110-116
uint256 rsethAmountToMint = _beforeDeposit(asset, depositAmount, minRSETHAmountExpected);

IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
_mintRsETH(rsethAmountToMint);
``` [1](#0-0) 

The protocol never reads its own balance before and after the transfer to confirm it actually received `depositAmount` tokens. `_beforeDeposit` delegates to `getRsETHAmountToMint`, which uses `depositAmount` directly:

```solidity
// contracts/LRTDepositPool.sol lines 519-520
rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
``` [2](#0-1) 

If the ERC20 token silently transfers fewer tokens than requested (fee-on-transfer), the protocol's actual TVL grows by `depositAmount − fee` while rsETH supply grows by the full `depositAmount` equivalent — identical in structure to M-06 where `mintCountTo(count)` was called and the outcome was trusted without verification.

The same unverified-input pattern appears in the L2 pool:

```solidity
// contracts/pools/RSETHPoolV3.sol lines 284-290
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount);
``` [3](#0-2) 

### Impact Explanation
Every deposit with a fee-on-transfer token mints rsETH worth more than the ETH value actually received. The rsETH supply grows faster than the underlying TVL, making the protocol insolvent. All existing rsETH holders are diluted proportionally. This maps to **Critical — Protocol insolvency** in the allowed impact scope.

### Likelihood Explanation
The admin controls the supported asset list via `LRTConfig`. However, the Foundation's own rationale for fixing M-06 was explicitly *not* about malicious actors but about "potential errors in implementation or misunderstanding of the interface requirements." The same applies here: a future LST or yield-bearing token with a non-obvious transfer tax could be added in good faith. The code contains no defensive check to catch this class of error, making the risk latent in every future asset onboarding decision.

### Recommendation
Mirror the M-06 fix: record the balance before the transfer, execute the transfer, then compute the actual received amount and use it for minting:

```diff
+ uint256 balanceBefore = IERC20(asset).balanceOf(address(this));
  IERC20(asset).safeTransferFrom(msg.sender, address(this), depositAmount);
+ uint256 actualReceived = IERC20(asset).balanceOf(address(this)) - balanceBefore;
+ if (actualReceived != depositAmount) revert UnexpectedTransferAmount();
  _mintRsETH(rsethAmountToMint);
```

Apply the same pattern to `RSETHPoolV3.deposit(address token, ...)` and `RSETHPoolV3ExternalBridge.deposit(address token, ...)`.

### Proof of Concept
1. Admin adds a token with a 1 % transfer fee as a supported asset in `LRTConfig`.
2. Alice calls `depositAsset(feeToken, 100e18, minRSETH, "")`.
3. `_beforeDeposit` computes `rsethAmountToMint` based on `100e18`.
4. `safeTransferFrom` delivers only `99e18` tokens to the pool (1 % fee burned/redirected).
5. `_mintRsETH(rsethAmountToMint)` mints rsETH priced against `100e18` tokens.
6. Protocol TVL increases by `99e18` tokens worth; rsETH supply increases by `100e18` tokens worth.
7. Repeated deposits accumulate insolvency; rsETH becomes under-collateralised and existing holders suffer losses when they withdraw. [4](#0-3) [5](#0-4)

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

**File:** contracts/LRTDepositPool.sol (L519-520)
```text
        // calculate rseth amount to mint based on asset amount and asset exchange rate
        rsethAmountToMint = (amount * lrtOracle.getAssetPrice(asset)) / lrtOracle.rsETHPrice();
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

**File:** contracts/pools/RSETHPoolV3.sol (L284-290)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```
