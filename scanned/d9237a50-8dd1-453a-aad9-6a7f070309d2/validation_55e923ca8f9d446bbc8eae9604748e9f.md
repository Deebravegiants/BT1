### Title
Fee-on-Transfer Token Causes Wrapper Over-Minting and Protocol Insolvency - (`contracts/L2/RsETHTokenWrapper.sol`, `contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

Both `RsETHTokenWrapper` and `AGETHTokenWrapper` mint wrapper tokens 1:1 with the caller-supplied `_amount` parameter without verifying the actual number of tokens received. If any allowed underlying token charges a transfer fee, the wrapper contract becomes undercollateralized: more wrapper tokens are minted than underlying tokens held, making it impossible for the last withdrawers to redeem their shares.

---

### Finding Description

In `_deposit`, both wrappers execute:

```solidity
ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
_mint(_to, _amount);
```

The mint amount is taken directly from the caller-supplied `_amount`, not from the actual balance delta. For a fee-on-transfer token, the contract receives `_amount - fee` but mints `_amount` wrapper tokens. Every deposit inflates the wrapper supply beyond the real backing.

The `_withdraw` path burns exactly `_amount` wrapper tokens and transfers exactly `_amount` underlying tokens:

```solidity
_burn(msg.sender, _amount);
ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
```

Because the contract holds less underlying than the total wrapper supply, the final withdrawers will receive a revert when the contract's underlying balance is exhausted, permanently freezing their wrapper tokens.

Contrast this with `KernelDepositPool.notifyRewardAmount`, which correctly uses a before/after balance check to handle fee-on-transfer tokens:

```solidity
uint256 balanceBefore = rewardsToken.balanceOf(address(this));
rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
uint256 balanceAfter = rewardsToken.balanceOf(address(this));
uint256 receivedAmount = balanceAfter - balanceBefore;
```

No such guard exists in either wrapper's `_deposit`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

---

### Impact Explanation

**Critical — Protocol insolvency / permanent freezing of funds.**

Each deposit with a fee-on-transfer token creates a deficit: wrapper supply exceeds actual backing. As users withdraw, the contract's underlying balance drains faster than wrapper supply decreases. The last holders of wrapper tokens cannot redeem them because `safeTransfer` will revert when the contract balance is insufficient. Their funds are permanently frozen inside the wrapper contract. [3](#0-2) 

---

### Likelihood Explanation

**Medium.** The `addAllowedToken` function in `RsETHTokenWrapper` (gated by `TIMELOCK_ROLE`) permits adding any ERC20 token to the allowed list at any time. Any future allowed token that charges a transfer fee — or any existing allowed token whose fee is later enabled (analogous to Tether's currently-zero fee) — immediately triggers the insolvency. The code contains no validation that an allowed token is non-fee-on-transfer. `AGETHTokenWrapper` has the same structural flaw. [5](#0-4) [6](#0-5) 

---

### Recommendation

Replace the fixed-`_amount` mint with an actual-received-amount mint using a before/after balance check, mirroring the pattern already used in `KernelDepositPool`:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    uint256 balanceBefore = ERC20Upgradeable(_asset).balanceOf(address(this));
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    uint256 received = ERC20Upgradeable(_asset).balanceOf(address(this)) - balanceBefore;

    _mint(_to, received);
    emit Deposit(_asset, msg.sender, _to, received);
}
```

Apply the same fix to `AGETHTokenWrapper._deposit`. Additionally, document that only non-fee-on-transfer, non-rebasing tokens should be added to the allowed list, and enforce this with an on-chain check or allowlist validation when adding tokens. [4](#0-3) 

---

### Proof of Concept

1. Admin adds `altRsETH_FeeToken` (a fee-on-transfer token with 1% fee) to `allowedTokens` via `addAllowedToken`.
2. Alice calls `deposit(altRsETH_FeeToken, 1000e18)`.
   - Contract receives `990e18` tokens (1% fee deducted).
   - Contract mints `1000e18` wrsETH to Alice.
3. Bob calls `deposit(altRsETH_FeeToken, 1000e18)`.
   - Contract receives `990e18` tokens.
   - Contract mints `1000e18` wrsETH to Bob.
   - Contract now holds `1980e18` underlying but has `2000e18` wrsETH outstanding.
4. Alice calls `withdraw(altRsETH_FeeToken, 1000e18)` — succeeds, contract now holds `980e18` underlying, `1000e18` wrsETH outstanding.
5. Bob calls `withdraw(altRsETH_FeeToken, 1000e18)` — **reverts** because contract only holds `980e18` but must transfer `1000e18`. Bob's `1000e18` wrsETH is permanently frozen. [1](#0-0) [2](#0-1)

### Citations

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

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-176)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
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

**File:** contracts/KERNEL/KernelDepositPool.sol (L573-577)
```text
        uint256 balanceBefore = rewardsToken.balanceOf(address(this));
        rewardsToken.safeTransferFrom(msg.sender, address(this), _amount);
        uint256 balanceAfter = rewardsToken.balanceOf(address(this));
        // Calculate the actual amount of tokens received in case of a transfer fee (tax)
        uint256 receivedAmount = balanceAfter - balanceBefore;
```
