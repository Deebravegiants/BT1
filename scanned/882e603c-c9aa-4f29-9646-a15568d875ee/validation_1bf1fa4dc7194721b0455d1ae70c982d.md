Looking at the three contracts carefully to trace the exact attack path.

### Title
Unbacked Wrapper Token Minting via AGETHPoolV3 Drains AGETHTokenWrapper altAgETH Reserves — (`contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

`AGETHTokenWrapper.mint()` mints canonical wrapper agETH tokens with no altAgETH deposit requirement. When `AGETHPoolV3` holds `MINTER_ROLE` on `AGETHTokenWrapper` (the intended L2 deployment where `AGETHPoolV3.agETH` = `AGETHTokenWrapper`), any user can deposit ETH into `AGETHPoolV3`, receive unbacked wrapper tokens, and immediately redeem them for altAgETH deposited by other users — draining the wrapper's reserves and causing insolvency.

---

### Finding Description

`AGETHTokenWrapper` enforces a 1:1 backing invariant: every wrapper agETH in circulation must be backed by an equal amount of altAgETH held by the contract. This invariant is maintained by `_deposit`, which requires `safeTransferFrom` of altAgETH before calling `_mint`: [1](#0-0) 

However, the privileged `mint` function bypasses this entirely: [2](#0-1) 

`AGETHPoolV3.deposit()` calls `agETH.mint(msg.sender, agETHAmount)` directly, depositing ETH into `AGETHPoolV3` (not into `AGETHTokenWrapper`): [3](#0-2) 

If `AGETHPoolV3.agETH` is `AGETHTokenWrapper` (the natural L2 deployment), `AGETHPoolV3` must hold `MINTER_ROLE` on `AGETHTokenWrapper` to function. Every ETH deposit to `AGETHPoolV3` then mints wrapper tokens with ETH backing held in `AGETHPoolV3`, not altAgETH backing held in `AGETHTokenWrapper`. The wrapper's `totalSupply()` grows while `altAgETH.balanceOf(address(wrapper))` does not.

`_withdraw` has no backing-ratio check — it simply burns wrapper tokens and transfers altAgETH: [4](#0-3) 

The attacker can then call `withdraw(altAgETH, agETHAmount)` to redeem the unbacked wrapper tokens for altAgETH deposited by legitimate users.

`maxAmountToDepositBridgerAsset` confirms the invariant break is observable — it returns `totalSupply() - balanceOfAssetInWrapper` as the deficit — but it is only used as a cap for `depositBridgerAssets` and does not block `withdraw`: [5](#0-4) 

---

### Impact Explanation

**Critical — Protocol insolvency.** The wrapper's altAgETH reserves are drained. Legitimate users who deposited altAgETH into the wrapper cannot redeem their canonical agETH for altAgETH. The ETH deposited to `AGETHPoolV3` remains in `AGETHPoolV3`, not in the wrapper, so there is no compensating collateral in the wrapper.

---

### Likelihood Explanation

Likelihood is **high** given the intended L2 deployment: `AGETHPoolV3` must hold `MINTER_ROLE` on `AGETHTokenWrapper` to function at all. No special role is required by the attacker — `AGETHPoolV3.deposit()` is a public payable function. Any user with ETH can execute the attack as soon as the wrapper holds any altAgETH balance.

---

### Recommendation

1. **Remove `MINTER_ROLE` from `AGETHPoolV3` on `AGETHTokenWrapper`.** `AGETHPoolV3` should use a separate agETH token (not the wrapper) as its mint target, or the pool should deposit altAgETH into the wrapper rather than minting unbacked tokens.
2. **Enforce backing in `mint`.** If `MINTER_ROLE` must be granted to pool contracts, `AGETHTokenWrapper.mint()` should require a simultaneous altAgETH deposit (similar to `_deposit`), or track a separate "bridge-minted" supply that is not redeemable for altAgETH.
3. **Add a backing check to `_withdraw`.** Revert if `altAgETH.balanceOf(address(this)) < amount` after the transfer, or enforce `totalSupply() <= altAgETH.balanceOf(address(this))` as an invariant at all exit points.

---

### Proof of Concept

```solidity
// Setup (L2 deployment):
// - AGETHTokenWrapper deployed as canonical agETH
// - AGETHPoolV3 deployed with agETH = address(wrapper)
// - AGETHPoolV3 granted MINTER_ROLE on wrapper
// - Alice deposits 100e18 altAgETH into wrapper, receives 100e18 wrapper agETH

// Attack:
// 1. Attacker deposits ETH to AGETHPoolV3
agETHPool.deposit{value: 1 ether}("ref");
// AGETHPoolV3 calls wrapper.mint(attacker, agETHAmount)
// wrapper.totalSupply() increases, but wrapper.altAgETH.balanceOf(wrapper) unchanged

// 2. Attacker withdraws altAgETH from wrapper using unbacked tokens
uint256 attackerBalance = wrapper.balanceOf(attacker); // agETHAmount from step 1
wrapper.withdraw(altAgETH, attackerBalance);
// _burn(attacker, attackerBalance) succeeds
// altAgETH.safeTransfer(attacker, attackerBalance) drains Alice's deposit

// Assert: Alice can no longer redeem her wrapper agETH for altAgETH
// wrapper.altAgETH.balanceOf(address(wrapper)) < wrapper.totalSupply()
// Alice's call to wrapper.withdraw(altAgETH, 100e18) reverts (insufficient balance)
```

### Citations

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

**File:** contracts/agETH/AGETHTokenWrapper.sol (L125-131)
```text
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, _to, _amount);
```

**File:** contracts/agETH/AGETHPoolV3.sol (L115-128)
```text
    function deposit(string memory referralId) external payable nonReentrant {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 agETHAmount, uint256 fee) = viewSwapAgETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        agETH.mint(msg.sender, agETHAmount);

        emit SwapOccurred(msg.sender, agETHAmount, fee, referralId);
    }
```
