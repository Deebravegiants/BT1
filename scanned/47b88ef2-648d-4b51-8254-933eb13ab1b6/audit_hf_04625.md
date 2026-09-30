# [M] `VaultBase` is not ERC4626 compliant

## Summary
Severity: Medium
Contest weight: 0.6307
Dataset id: 22295
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of a systematic deviation from the ERC4626 tokenized vault standard in the VaultBase contract and its MultiStrategy extension. The root cause is that several mandatory view functions – maxDeposit, maxMint, maxWithdraw, maxRedeem, previewMint, previewWithdraw and previewRedeem – are implemented in a way that ignores global or per‑account limits, contract pause state, and withdrawal fees, and they use rounding‑down arithmetic where the specification requires rounding‑up. As a result, the contract reports overly optimistic deposit caps, underestimates the amount of assets required for minting, and provides inaccurate preview values that do not include fees or rounding loss. An attacker or an unsuspecting integrator can exploit this mismatch by relying on the view functions to calculate how much they can deposit, mint, withdraw or redeem. Because the functions claim that unlimited assets can be deposited (returning type(uint256).max) even when a per‑wallet limit is set or the vault is paused, a transaction may revert later in the internal deposit logic, causing a failed deposit after the user has already approved token transfers. Similarly, previewWithdraw and previewRedeem return values that are lower than the actual shares that will be burned, so a user may think they will receive a certain amount of underlying tokens but end up receiving less after fees are applied. The impact includes broken external integrations that depend on ERC4626 compliance, unexpected transaction reverts, users receiving fewer assets than expected, and potential accounting discrepancies when multiple strategies are involved because rounding loss is not reflected in previewRedeem. The issue manifests whenever the vault is paused, when a max‑deposit limit is configured, when withdrawal fees are active, or when the MultiStrategy vault aggregates assets across several strategies. All users, third‑party protocols, and the protocol itself are affected because the contract violates the accounting guarantees of ERC4626, breaking the trust model of tokenized vaults. The problem was discovered during a Code4rena audit that compared the contract’s public view functions against the ERC4626 specification and identified mismatches. It can be hard to notice because the faulty functions are read‑only and do not revert, so they may pass basic unit tests that only cover successful paths, while off‑chain callers receive misleading numbers. To remediate, the contract must be updated so that maxDeposit and maxMint respect pause state and any configured per‑wallet caps, returning zero when deposits are disabled; maxWithdraw and maxRedeem must also return zero when withdrawals are disabled. Preview functions must round up and incorporate any withdrawal fees, and previewRedeem for the MultiStrategy vault must simulate the multi‑strategy withdrawal flow to account for rounding loss. In short, the contract should be brought into full ERC4626 compliance by aligning its view logic with the specification’s safety and accounting requirements.

## Proof of Concept
The official ERC4626 specifications can be found on this [page](https://eips.ethereum.org/EIPS/eip-4626). Several required specifications are not being followed. Here are the incorrectly implemented functions:

**`maxDeposit`**

Maximum amount of the underlying asset that can be deposited into the Vault for the `receiver`, through a `deposit` call. MUST return the maximum amount of assets `deposit` would allow to be deposited for `receiver` and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted (it should underestimate if necessary). This assumes that the user has infinite assets, i.e. MUST NOT rely on `balanceOf` of `asset`. MUST factor in both global and user-specific limits, like if deposits are entirely disabled (even temporarily) it MUST return 0.

`VaultBase.maxDeposit` always returns `type(uint256).max`. However, `_depositInternal` uses `getMaxDeposit` to enforce limits. This means `VaultBase.maxDeposit` returns incorrect values if `getMaxDeposit` was set. Additionally, it doesn’t return 0 when the contract is paused.

```solidity
function maxDeposit(address) external pure override returns (uint256 maxAssets) {
    return type(uint256).max;
}

function _depositInternal(uint256 assets, address receiver) private returns (uint256 shares) {
    ...
    // Check if deposit exceeds the maximum allowed per wallet
    uint256 maxDepositLocal = getMaxDeposit();
    if (maxDepositLocal > 0) {
        uint256 depositInAssets = (balanceOf(msg.sender) * _ONE) / tokenPerAsset();
        uint256 newBalance = assets + depositInAssets;
        if (newBalance > maxDepositLocal) revert MaxDepositReached();
    }
    ...
}
```

**`maxMint`**

Maximum amount of shares that can be minted from the Vault for the `receiver`, through a `mint` call. MUST return the maximum amount of shares `mint` would allow to be deposited to `receiver` and not cause a revert, which MUST NOT be higher than the actual maximum that would be accepted (it should underestimate if necessary). This assumes that the user has infinite assets, i.e. MUST NOT rely on `balanceOf` of `asset`. MUST factor in both global and user-specific limits, like if mints are entirely disabled (even temporarily) it MUST return 0.

`VaultBase.maxMint` always returns `type(uint256).max`. However, `_depositInternal` uses `getMaxDeposit` to enforce limits. This means `VaultBase.maxMint` returns incorrect values if `getMaxDeposit` was set. Additionally, it doesn’t return 0 when the contract is paused.

```solidity
function maxMint(address) external pure override returns (uint256 maxShares) {
    return type(uint256).max;
}

function _depositInternal(uint256 assets, address receiver) private returns (uint256 shares) {
    ...

    // Check if deposit exceeds the maximum allowed per wallet
    uint256 maxDepositLocal = getMaxDeposit();
    if (maxDepositLocal > 0) {
        uint256 depositInAssets = (balanceOf(msg.sender) * _ONE) / tokenPerAsset();
        uint256 newBalance = assets + depositInAssets;
        if (newBalance > maxDepositLocal) revert MaxDepositReached();
    }

    ...
}
```

**`maxWithdraw`**

MUST factor in both global and user-specific limits, like if withdrawals are entirely disabled (even temporarily) it MUST return 0.

`VaultBase.maxWithdraw` doesn’t return 0 when the contract is paused.

```solidity
function maxWithdraw(address shareHolder) external view override returns (uint256 maxAssets) {
    maxAssets = this.convertToAssets(balanceOf(shareHolder));
}
```

**`maxRedeem`**

MUST factor in both global and user-specific limits, like if redemption is entirely disabled (even temporarily) it MUST return 0.

`VaultBase.maxRedeem` doesn’t return 0 when the contract is paused.

```solidity
function maxRedeem(address shareHolder) external view override returns (uint256 maxShares) {
    maxShares = balanceOf(shareHolder);
}
```

**`previewMint`**

MUST return as close to and no fewer than the exact amount of assets that would be deposited in a `mint` call in the same transaction. i.e. `mint` should return the same or fewer `assets` as `previewMint` if called in the same transaction.

If (1) it’s calculating the amount of shares a user has to supply to receive a given amount of the underlying tokens or (2) it’s calculating the amount of underlying tokens a user has to provide to receive a certain amount of shares, it should round _up_.

It is recommended that `previewMint` rounds up the results. ([reference](https://eips.ethereum.org/EIPS/eip-4626#security-considerations)) It should return no less than the amount of assets the user actually should pay. But `VaultBase.previewMint` rounds down results.

```solidity
function previewMint(uint256 shares) external view override returns (uint256 assets) {
    assets = this.convertToAssets(shares);
}
```

**`previewWithdraw`**

MUST return as close to and no fewer than the exact amount of Vault shares that would be burned in a withdraw call in the same transaction. i.e. withdraw should return the same or fewer shares as previewWithdraw if called in the same transaction. MUST be inclusive of withdrawal fees. Integrators should be aware of the existence of withdrawal fees.

If (1) it’s calculating the amount of shares a user has to supply to receive a given amount of the underlying tokens or (2) it’s calculating the amount of underlying tokens a user has to provide to receive a certain amount of shares, it should round _up_.

VaultBase takes a fee when you withdraw, but `VaultBase.previewWithdraw` doesn’t count the fee. `previewWithdraw` should return the share including the fee. Also, `previewWithdraw` is recommended to round up the result ([reference](https://eips.ethereum.org/EIPS/eip-4626#security-considerations)), but `VaultBase.previewWithdraw` is rounding down the calculation.

```solidity
function previewWithdraw(uint256 assets) external view override returns (uint256 shares) {
    shares = this.convertToShares(assets);
}

function convertToShares(uint256 assets) external view override returns (uint256 shares) {
    Rebase memory total = Rebase(totalAssets(), totalSupply());
    shares = total.toBase(assets, false);
}

function _redeemInternal(
    uint256 shares,
    address receiver,
    address holder,
    bool shouldRedeemETH
) private returns (uint256 retAmount) {
    ...

    // Calculate and handle withdrawal fees
    if (getWithdrawalFee() != 0 && getFeeReceiver() != address(0)) {
        fee = amount.mulDivUp(getWithdrawalFee(), PERCENTAGE_PRECISION);

        if (shouldRedeemETH && _asset() == wETHA()) {
            unwrapETH(amount);
            payable(receiver).sendValue(amount - fee);
            payable(getFeeReceiver()).sendValue(fee);
        } else {
            IERC20Upgradeable(_asset()).transfer(receiver, amount - fee);
            IERC20Upgradeable(_asset()).transfer(getFeeReceiver(), fee);
        }
    } else {
        ...
    }

    emit Withdraw(msg.sender, receiver, holder, amount - fee, shares);
    retAmount = amount - fee;
}
```

**`previewRedeem`**

MUST return as close to and no more than the exact amount of assets that would be withdrawn in a `redeem` call in the same transaction. i.e. `redeem` should return the same or more `assets` as `previewRedeem` if called in the same transaction. MUST be inclusive of withdrawal fees. Integrators should be aware of the existence of withdrawal fees.

VaultBase charges withdrawal fees but `VaultBase.previewRedeem` doesn’t include fees. It should deduct the asset amount paid as fees.

Additionally, when withdrawing from MultiStrategyVault, amounts to undeploy are calculated per Strategy with rounding down. Since `previewRedeem`’s result shouldn’t exceed actual withdrawal amount, it should simulate multi-Strategy withdrawals to include losses.

```solidity
function previewRedeem(uint256 shares) external view override returns (uint256 assets) {
    assets = this.convertToAssets(shares);
}
```

## Recommendation
Modify to comply with the specification of ERC4626. For `MultiStrategyVault`, override ERC4626 view functions to simulate `multi-Strategy` deposits/withdrawals and include rounding loss.

**chefkenji (BakerFi) confirmed**

[PR-27](https://github.com/baker-fi/bakerfi-contracts/pull/27)
