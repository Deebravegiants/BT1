### Title
Fee-on-Transfer Token Mis-Accounting in `_deposit` Mints Excess Wrapper Tokens, Causing Insolvency - (`contracts/L2/RsETHTokenWrapper.sol`, `contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

Both `RsETHTokenWrapper._deposit` and `AGETHTokenWrapper._deposit` call `safeTransferFrom` with `_amount` and immediately mint `_amount` wrapper tokens to the recipient, without verifying the actual balance increase. If the deposited token charges a transfer fee, the contract receives fewer tokens than `_amount` but mints the full `_amount` of wrapper tokens, creating an insolvency condition where total wrapper supply exceeds the underlying collateral held.

---

### Finding Description

In `RsETHTokenWrapper._deposit`:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

    _mint(_to, _amount);  // mints _amount regardless of actual tokens received
    emit Deposit(_asset, msg.sender, _to, _amount);
}
```

The same pattern exists identically in `AGETHTokenWrapper._deposit`.

No balance-before/after check is performed. If the underlying `_asset` token deducts a fee on transfer, the contract receives `_amount - fee` tokens but mints `_amount` wrapper tokens. Each such deposit widens the gap between `totalSupply()` of wrapper tokens and the actual underlying token balance held by the contract.

The `_withdraw` function then burns `_amount` wrapper tokens and transfers `_amount` underlying tokens:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
}
```

Since the contract holds less underlying than the total wrapper supply, the last withdrawers will find the contract unable to fulfill their redemptions, permanently freezing their funds.

The `allowedTokens` mapping in `RsETHTokenWrapper` can be extended by `TIMELOCK_ROLE` via `addAllowedToken`, meaning new fee-on-transfer tokens can be added to the system. Even for the initially configured tokens, if any bridge variant of rsETH/agETH introduces a fee mechanism (e.g., via an upgrade), the vulnerability is immediately exploitable by any depositor.

---

### Impact Explanation

Every deposit with a fee-on-transfer token over-mints wrapper tokens relative to the actual collateral held. The cumulative shortfall grows with each deposit. When the contract's underlying token balance is exhausted, subsequent `withdraw` or `withdrawTo` calls revert, permanently freezing the wrapper tokens of the last holders. This constitutes **protocol insolvency** within the wrapper contract and **permanent freezing of funds** for affected users.

**Impact: Critical** — permanent freezing of funds / protocol insolvency in the wrapper.

---

### Likelihood Explanation

The `allowedTokens` mapping in `RsETHTokenWrapper` is extensible via `addAllowedToken` (callable by `TIMELOCK_ROLE`). Any future allowed token that charges a transfer fee triggers the vulnerability. Additionally, the initially configured altRsETH/altAgETH tokens are bridge-wrapped tokens whose underlying implementations could be upgraded. Any unprivileged depositor calling `deposit` or `depositTo` with a fee-on-transfer allowed token is the attacker-controlled entry path — no special role is required beyond holding the token.

**Likelihood: Medium** — requires a fee-on-transfer token to be in the allowed set, which is possible via governance or token upgrade.

---

### Recommendation

In both `_deposit` functions, record the contract's balance of `_asset` before the transfer and compute the actual received amount from the balance delta. Mint only the actual received amount:

```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();

    uint256 balanceBefore = ERC20Upgradeable(_asset).balanceOf(address(this));
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    uint256 actualReceived = ERC20Upgradeable(_asset).balanceOf(address(this)) - balanceBefore;

    _mint(_to, actualReceived);
    emit Deposit(_asset, msg.sender, _to, actualReceived);
}
```

Apply the same fix to `AGETHTokenWrapper._deposit`.

---

### Proof of Concept

1. A fee-on-transfer token (e.g., 1% fee) is added to `allowedTokens` in `RsETHTokenWrapper` via `addAllowedToken`.
2. Alice calls `deposit(feeToken, 1000e18)`.
3. `safeTransferFrom` transfers 1000e18 from Alice, but the contract only receives 990e18 (1% fee deducted).
4. `_mint(Alice, 1000e18)` mints 1000e18 wrsETH to Alice.
5. Bob calls `deposit(feeToken, 1000e18)` — contract now holds 1980e18 underlying, but 2000e18 wrsETH is in circulation.
6. Alice calls `withdraw(feeToken, 1000e18)` — succeeds, contract now holds 980e18 underlying, 1000e18 wrsETH outstanding.
7. Bob calls `withdraw(feeToken, 1000e18)` — reverts because the contract only holds 980e18 but must transfer 1000e18. Bob's 1000e18 wrsETH is permanently frozen.

**Root cause lines:** [1](#0-0) [2](#0-1)

### Citations

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
