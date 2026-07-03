### Title
Wrapper Allows Arbitrary Allowed-Token Withdrawal Without Accounting for Per-Token Collateral, Enabling Cross-Token Drain - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary

`RsETHTokenWrapper` maintains a flat `allowedTokens` mapping that treats every allowed rsETH variant as interchangeable 1:1 with `wrsETH`. Because `_deposit` mints `wrsETH` 1:1 for **any** allowed token and `_withdraw` burns `wrsETH` and releases **any** allowed token 1:1, a user who deposits a lower-value allowed token can withdraw a higher-value allowed token, draining other depositors' collateral.

### Finding Description

`RsETHTokenWrapper` is designed to wrap "alternative rsETH tokens" from multiple L2 chains into a single canonical `wrsETH`. The contract tracks which tokens are acceptable via a single flat mapping: [1](#0-0) 

Deposit mints `wrsETH` 1:1 for any allowed token: [2](#0-1) 

Withdrawal burns `wrsETH` and releases **any caller-chosen** allowed token 1:1: [3](#0-2) 

There is no per-token accounting of how much of each allowed token backs the outstanding `wrsETH` supply. The contract never checks whether the specific token being withdrawn is actually present in sufficient quantity relative to what was deposited. Any holder of `wrsETH` — regardless of which token they originally deposited — can freely choose which allowed token to redeem.

The `maxAmountToDepositBridgerAsset` function compounds this by computing headroom per-asset in isolation, ignoring the balances of all other allowed tokens: [4](#0-3) 

If two allowed tokens are present (e.g., `rsETH_A` balance = 0, `rsETH_B` balance = 100, `wrsETHSupply` = 100), the function returns 100 for `rsETH_A`, allowing the bridger to over-collateralize with `rsETH_A` while `rsETH_B` remains fully withdrawable by any `wrsETH` holder.

### Impact Explanation

If two allowed tokens trade at different prices (e.g., one rsETH variant depegs on its source chain while the other does not), an attacker can:

1. Deposit `N` units of the cheaper token → receive `N` `wrsETH`.
2. Call `withdraw(expensiveToken, N)` → burn `N` `wrsETH`, receive `N` units of the more expensive token.

The attacker extracts the price difference from the pool of tokens deposited by honest users. At scale this fully drains the more valuable token from the wrapper. This is a direct, at-rest theft of user funds — **Critical** impact.

### Likelihood Explanation

The wrapper is explicitly designed to hold multiple allowed rsETH variants (`reinitialize` adds a second token; `addAllowedToken` is a normal TIMELOCK operation, not a compromise). Any transient price divergence between two allowed tokens — caused by bridge latency, liquidity imbalance, or a partial depeg on one chain — opens the window. No privileged key compromise is required; any `wrsETH` holder can execute the attack permissionlessly via the public `withdraw` / `withdrawTo` functions. [5](#0-4) 

### Recommendation

Track per-token collateral separately. Maintain a `mapping(address => uint256) public tokenDeposited` that records how much of each allowed token backs the supply. On `_withdraw`, verify that `tokenDeposited[_asset] >= _amount` before releasing the asset, and decrement accordingly. On `_deposit`, increment `tokenDeposited[_asset]`. This ensures that `wrsETH` minted against token A can only be redeemed for token A, mirroring the fix applied in the Linea bridge (per-layer mappings).

### Proof of Concept

**Setup**: Admin calls `addAllowedToken(rsETH_A)` and `addAllowedToken(rsETH_B)`. Both are allowed. `rsETH_B` trades at 1.05× the value of `rsETH_A` due to market conditions.

**Attack**:
1. Attacker calls `deposit(rsETH_A, 1000e18)` → wrapper receives 1000 `rsETH_A`, mints 1000 `wrsETH` to attacker.
2. Honest users have previously deposited 1000 `rsETH_B` into the wrapper (also minted 1000 `wrsETH`).
3. Attacker calls `withdraw(rsETH_B, 1000e18)` → wrapper burns 1000 `wrsETH`, transfers 1000 `rsETH_B` to attacker.
4. Attacker holds 1000 `rsETH_B` (worth 1050 ETH equivalent) having spent only 1000 `rsETH_A` (worth 1000 ETH equivalent). Net theft: 50 ETH equivalent from honest depositors.

The `_withdraw` function performs no check that the caller's `wrsETH` was minted against `rsETH_B`; it only checks `allowedTokens[rsETH_B] == true`, which is satisfied. [3](#0-2)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L24-24)
```text
    mapping(address allowedToken => bool isAllowed) public allowedTokens;
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L84-94)
```text
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
    }

    /// @dev Withdraw altRsETH tokens from wrsETH to a user
    /// @param asset The address of the token to withdraw
    /// @param _to The user to withdraw to
    /// @param _amount The amount of tokens to withdraw
    function withdrawTo(address asset, address _to, uint256 _amount) external {
        _withdraw(asset, _to, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L99-110)
```text
    function maxAmountToDepositBridgerAsset(address _asset) public view returns (uint256) {
        if (!allowedTokens[_asset]) return 0;

        // get totalSupply of wrsETH minted
        uint256 wrsETHSupply = totalSupply();
        // balance of _asset with the contract
        uint256 balanceOfAssetInWrapper = ERC20Upgradeable(_asset).balanceOf(address(this));

        if (balanceOfAssetInWrapper > wrsETHSupply) return 0;

        return wrsETHSupply - balanceOfAssetInWrapper;
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-128)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
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
