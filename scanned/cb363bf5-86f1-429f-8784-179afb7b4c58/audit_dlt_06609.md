# [M] wstX.sol contract deposit(), mint(), withdraw() and redeem() functions are not incomplaince with ERC4626

## Summary
Severity: Medium
Chain: Smart contract
Component: Accumulated-finance
Published: 2024-09-11
Source: https://github.com/hats-finance/Accumulated-finance-0x75278bcc0fa7c9e3af98654bce195eaf3bb6a784/issues/65
Type: hats-finding

## Details
**Github username:** @0xRizwan
**Twitter username:** 0xRizwann
**Submission hash (on-chain):** 0x2b1e989f7e706213581585c76a599ab7c9b5daa5dac1eefd1d23626837dbe6d4
**Severity:** medium

**Description:**
### Title
`wstX.sol` contract `deposit()`, `mint()`, `withdraw()` and `redeem()` functions are not incomplaince with `ERC4626`

### Severity
Medium

### Affected contracts
wrstMTRG.sol, wstARB.sol, wstDOJ.sol, wstMANTA.sol, wstMETIS.sol, wstROSE.sol, wstVLX.sol, wstZETA.sol and wstToken.sol

### Vulnerability details
`wstX` has used solmate's ERC4626 as base contract. `wstX` contracts herein referred as `wstTokenV2.sol` mentions to be ERC4626 fully compliant which can be checked [here](https://github.com/AccumulatedFinance/contracts-v2/blob/ef89e73c9d86f086dfc9dd379cb395c1368642cd/contracts/wstTokenV2.sol#L884) and [here](https://github.com/AccumulatedFinance/contracts-v2/blob/ef89e73c9d86f086dfc9dd379cb395c1368642cd/contracts/wstTokenV2.sol#L1050)

>     It is fully compatible with [ERC4626](https://eips.ethereum.org/EIPS/eip-4626) allowing for DeFi composability

>     wstToken adheres to ERC-4626 vault specs 

The `deposit()`, `withdraw()`, `redeem()` and `mint()` functions of `wstX` contract is not incompliance with ERC4626.

For understanding:

Lets check `redeem()` function which is used to redeem a specific number of shares from owner and sends assets of underlying token from the vault to receiver and it is implemented as:

```solidity
    function redeem(
        uint256 shares,
        address receiver,
        address owner
    ) public virtual returns (uint256 assets) {
        if (msg.sender != owner) {
            uint256 allowed = allowance[owner][msg.sender]; // Saves gas for limited approvals.

            if (allowed != type(uint256).max) allowance[owner][msg.sender] = allowed - shares;
        }

        // Check for rounding error since we round down in previewRedeem.
        require((assets = previewRedeem(shares)) != 0, "ZERO_ASSETS");

        beforeWithdraw(assets, shares);

        _burn(owner, shares);

        emit Withdraw(msg.sender, receiver, owner, assets, shares);

        asset.safeTransfer(receiver, assets);
    }
``` 

and `maxRedeem()` function returns the maximum amount of shares that can be redeemed from the owner balance through a redeem() call.

```solidity
    function maxRedeem(address owner) public view virtual returns (uint256) {
        return balanceOf[owner];
    }
```

The issue here is that, [redeem](https://eips.ethereum.org/EIPS/eip-4626)() function is not incompliance with ERC4626 as ERC4626 deposit specification states,

redeem

> MUST revert if all of shares cannot be redeemed (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).

It means that, the `maxRedeem` limit is not checked in redeem() function. redeem() will not revert if the owner shares maximum limit to redeem is reached

`maxRedeem()` function is implemented in `wstX` contracts but its not checked in redeem() function.

Similarly, withdraw(), deposit() and mint() are also not incompliance with ERC4626. Below specification related to them is not complied in functions.

deposit
> MUST revert if all of assets cannot be deposited (due to deposit limit being reached, slippage, the user not approving enough underlying tokens to the Vault contract, etc).

mint
> MUST revert if all of shares cannot be minted (due to deposit limit being reached, slippage, the user not approving enough underlying tokens to the Vault contract, etc).

withdraw
> MUST revert if all of assets cannot be withdrawn (due to withdrawal limit being reached, slippage, the owner not having enough shares, etc).

ERC4626 link- https://eips.ethereum.org/EIPS/eip-4626

### Impact
Failure to comply with the ERC4626 deposit, withdraw, redeem and mint specification which is considered as fully compliance by `wstX` contracts.

### Recommendation
Ensure `wstX` contracts deposit, withdraw, redeem and mint function must be incompliance with ERC4626.

For example understanding,

consider below changes for deposit():

```diff
+  error wstTokenExceededMaxDeposit(address receiver, uint256 assets, uint256 max);
+  error wstTokenExceededMaxMint(address receiver, uint256 shares, uint256 max);
+  error wstTokenExceededMaxWithdraw(address owner, uint256 assets, uint256 max);
+  error wstTokenExceededMaxRedeem(address owner, uint256 shares, uint256 max);

    . . . some code . . .     
    
    function deposit(uint256 assets, address receiver) public virtual returns (uint256 shares) {
+     uint256 maxAssets = maxDeposit(receiver);
+        if (assets > maxAssets) {
+            revert wstTokenExceededMaxDeposit(receiver, assets, maxAssets);
+        }

        // Check for rounding error since we round down in previewDeposit.
        require((shares = previewDeposit(assets)) != 0, "ZERO_SHARES");

        // Need to transfer before minting or ERC777s could reenter.
        asset.safeTransferFrom(msg.sender, address(this), assets);

        _mint(receiver, shares);

        emit Deposit(msg.sender, receiver, assets, shares);

        afterDeposit(assets, shares);
    }
    
    function mint(uint256 shares, address receiver) public virtual returns (uint256 assets) {
+        uint256 maxShares = maxMint(receiver);
+        if (shares > maxShares) {
+            revert wstTokenExceededMaxMint(receiver, shares, maxShares);
+        }    
    
        assets = previewMint(shares); // No need to check for rounding error, previewMint rounds up.

        // Need to transfer before minting or ERC777s could reenter.
        asset.safeTransferFrom(msg.sender, address(this), assets);

        _mint(receiver, shares);

        emit Deposit(msg.sender, receiver, assets, shares);

        afterDeposit(assets, shares);
    }

    function withdraw(
        uint256 assets,
        address receiver,
        address owner
    ) public virtual returns (uint256 shares) {
+        uint256 maxAssets = maxWithdraw(owner);
+        if (assets > maxAssets) {
+            revert wstTokenExceededMaxWithdraw(owner, assets, maxAssets);
+        }
        
        shares = previewWithdraw(assets); // No need to check for rounding error, previewWithdraw rounds up.

        if (msg.sender != owner) {
            uint256 allowed = allowance[owner][msg.sender]; // Saves gas for limited approvals.

            if (allowed != type(uint256).max) allowance[owner][msg.sender] = allowed - shares;
        }

        beforeWithdraw(assets, shares);

        _burn(owner, shares);

        emit Withdraw(msg.sender, receiver, owner, assets, shares);

        asset.safeTransfer(receiver, assets);
    }

    function redeem(
        uint256 shares,
        address receiver,
        address owner
    ) public virtual returns (uint256 assets) {
+        uint256 maxShares = maxRedeem(owner);
+        if (shares > maxShares) {
+            revert wstTokenExceededMaxRedeem(owner, shares, maxShares);
+        }
        
        if (msg.sender != owner) {
            uint256 allowed = allowance[owner][msg.sender]; // Saves gas for limited approvals.

            if (allowed != type(uint256).max) allowance[owner][msg.sender] = allowed - shares;
        }

        // Check for rounding error since we round down in previewRedeem.
        require((assets = previewRedeem(shares)) != 0, "ZERO_ASSETS");

        beforeWithdraw(assets, shares);

        _burn(owner, shares);

        emit Withdraw(msg.sender, receiver, owner, assets, shares);

        asset.safeTransfer(receiver, assets);
    }
 ```

### Additional notes
Solmate has officially opened max check issues [here](https://github.com/transmissions11/solmate/issues/362).
