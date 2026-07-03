### Title
Deflationary/Fee-on-Transfer Token Support Causes Undercollateralization in AGETHTokenWrapper and RSETHPoolV3 Deposit Paths - (File: contracts/agETH/AGETHTokenWrapper.sol, contracts/pools/RSETHPoolV3.sol)

### Summary
`AGETHTokenWrapper._deposit` and `RSETHPoolV3.deposit(token, amount, referralId)` both mint shares based on the nominal `amount` parameter without verifying the actual tokens received after `safeTransferFrom`. For fee-on-transfer or deflationary tokens, the contract receives fewer tokens than `amount` but mints the full share amount, creating undercollateralization that grows with every deposit.

### Finding Description

**AGETHTokenWrapper._deposit** (primary instance):

The internal `_deposit` function, called by the public `deposit` and `depositTo` entry points, performs a `safeTransferFrom` for `_amount` and then unconditionally mints exactly `_amount` agETH wrapper tokens:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_to, _amount);          // mints _amount regardless of actual received
    emit Deposit(_asset, _to, _amount);
}
``` [1](#0-0) 

The corresponding `_withdraw` function burns `_amount` agETH and transfers exactly `_amount` of the underlying token back:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    ...
}
``` [2](#0-1) 

If the underlying `_asset` charges a transfer fee, the contract receives `_amount - fee` tokens but mints `_amount` agETH. Each deposit widens the gap between agETH supply and actual token reserves. Eventually, the last withdrawers cannot redeem their agETH because the contract holds fewer tokens than the outstanding agETH supply.

**RSETHPoolV3.deposit(token, amount, referralId)** (secondary instance):

The same pattern appears in the pool's token deposit path. The pool transfers `amount` from the user, then computes and mints `rsETHAmount` of wrsETH based on the nominal `amount`, not the actual received balance:

```solidity
IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
(uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);
feeEarnedInToken[token] += fee;
wrsETH.mint(msg.sender, rsETHAmount);
``` [3](#0-2) 

The same pattern is replicated in `RSETHPoolV3ExternalBridge` and `RSETHPoolV3WithNativeChainBridge`: [4](#0-3) 

### Impact Explanation

**AGETHTokenWrapper**: The wrapper is designed as a 1:1 collateralized token. Undercollateralization means the last agETH holders cannot redeem their tokens — a permanent partial freeze of funds for those users. The `maxAmountToDepositBridgerAsset` invariant (`agETHSupply - balanceOfAssetInWrapper`) is also corrupted, allowing the bridger to over-deposit and further worsening the shortfall. [5](#0-4) 

**RSETHPoolV3**: The pool's token reserves back the minted wrsETH. Undercollateralization means the pool cannot fully honor reverse swaps or bridger asset movements, causing a shortfall for wrsETH holders.

Impact: **Low** — Contract fails to deliver promised returns (1:1 redemption) without direct theft; escalates to **Medium** (temporary freezing of funds) for the last depositors who cannot withdraw.

### Likelihood Explanation

The allowed tokens in `AGETHTokenWrapper` are set at initialization to specific alt-agETH tokens and can only be removed by admin, not added. The supported tokens in `RSETHPoolV3` are admin-controlled. If any allowed/supported token carries a transfer fee (including future token upgrades or bridged variants with fee mechanisms), the vulnerability is triggered by any ordinary depositor calling the public `deposit`/`depositTo` functions — no privileged action is required at deposit time. [6](#0-5) 

### Recommendation

Use a balance-before/balance-after pattern to determine the actual amount received, and mint shares based on the actual received amount:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    uint256 balanceBefore = ERC20Upgradeable(_asset).balanceOf(address(this));
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    uint256 actualReceived = ERC20Upgradeable(_asset).balanceOf(address(this)) - balanceBefore;
    _mint(_to, actualReceived);
    emit Deposit(_asset, _to, actualReceived);
}
```

Apply the same fix to `RSETHPoolV3.deposit(token, amount, referralId)` and its sibling pool contracts, computing `rsETHAmount` from `actualReceived` rather than `amount`.

### Proof of Concept

1. Deploy `AGETHTokenWrapper` with an alt-agETH token that charges a 1% transfer fee.
2. Alice calls `deposit(asset, 1000e18)`. Contract receives 990e18 tokens but mints 1000e18 agETH to Alice.
3. Bob calls `deposit(asset, 1000e18)`. Contract receives 990e18 tokens but mints 1000e18 agETH to Bob.
4. Contract holds 1980e18 tokens, but 2000e18 agETH is outstanding.
5. Alice calls `withdraw(asset, 1000e18)`. Burns 1000e18 agETH, transfers 1000e18 tokens (another fee deduction means she receives ~990e18, but the contract now holds only ~980e18).
6. Bob attempts `withdraw(asset, 1000e18)`. Contract holds ~980e18 tokens but must transfer 1000e18 — the call reverts. Bob's funds are permanently frozen. [1](#0-0) [2](#0-1)

### Citations

**File:** contracts/agETH/AGETHTokenWrapper.sol (L60-70)
```text
    function deposit(address asset, uint256 _amount) external {
        _deposit(asset, msg.sender, _amount);
    }

    /// @dev Deposit altAgETH for agETH to a user
    /// @param asset The address of the token to deposit
    /// @param _to The user to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
    function depositTo(address asset, address _to, uint256 _amount) external {
        _deposit(asset, _to, _amount);
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L90-101)
```text
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrapped agETH minted
        uint256 agETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > agETHSupply) return 0;

        return agETHSupply - balanceOfAssetInWrapper;
    }
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L111-119)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, _to, _amount);
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

**File:** contracts/pools/RSETHPoolV3.sol (L284-290)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L403-409)
```text
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);
```
