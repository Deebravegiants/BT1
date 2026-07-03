### Title
Arbitrary Token Selection in `_withdraw` Enables Cross-Token Drain — (`File: contracts/L2/RsETHTokenWrapper.sol`)

---

### Summary

`RsETHTokenWrapper` supports multiple allowed altRsETH tokens and mints `wrsETH` 1:1 for any of them. However, `_withdraw` only checks that the requested output token is in `allowedTokens`; it never verifies that the caller is redeeming the same token they deposited. An attacker can deposit a depegged or cheaper altRsETH variant, receive `wrsETH`, then withdraw the more valuable canonical rsETH held in the contract — directly stealing funds from other depositors.

---

### Finding Description

`RsETHTokenWrapper` maintains an `allowedTokens` mapping that can hold multiple distinct altRsETH token addresses. The `reinitialize` function explicitly adds a second token, and `addAllowedToken` (gated by `TIMELOCK_ROLE`) can add more. [1](#0-0) [2](#0-1) [3](#0-2) 

`_deposit` mints `wrsETH` 1:1 for whichever allowed token is provided: [4](#0-3) 

`_withdraw` burns `wrsETH` and transfers whichever allowed token the caller requests — with no check that it matches the deposited token:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();  // only checks whitelist
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);   // transfers any allowed token
    emit Withdraw(_asset, msg.sender, _to, _amount);
}
``` [5](#0-4) 

Because `wrsETH` is fungible and carries no record of which underlying token was deposited, any `wrsETH` holder can freely choose which allowed token to redeem. If two allowed tokens trade at different prices (e.g., one is depegged), the attacker profits by depositing the cheap token and withdrawing the expensive one.

---

### Impact Explanation

**Critical — direct theft of user funds.**

Any `wrsETH` holder can drain the more valuable altRsETH token from the contract. Legitimate depositors of the canonical rsETH lose their principal; the attacker extracts the price difference for every unit they cycle through the wrapper. The attack scales linearly with the balance of the more valuable token held by the contract.

---

### Likelihood Explanation

**High.** The `reinitialize` function was already used to add a second allowed token, confirming the multi-token scenario is an intended operational state. [2](#0-1) 

Any time two allowed tokens diverge in market price — even temporarily due to bridge delays, liquidity events, or a partial depeg — the attack becomes immediately profitable. No privileged access is required; any unprivileged user holding or able to acquire `wrsETH` can execute it.

---

### Recommendation

Track which token each unit of `wrsETH` was minted against, or restrict the wrapper to a single canonical token at a time. If multiple tokens must be supported simultaneously, enforce that `withdraw(asset, amount)` can only redeem the same token that was deposited (e.g., via per-user per-token accounting), or price-weight the mint/burn so that 1 unit of a cheaper token mints fewer `wrsETH` than 1 unit of the canonical token.

---

### Proof of Concept

1. The wrapper holds 1000 canonical rsETH (token A, worth $1.00 each) deposited by legitimate users.
2. A depegged altRsETH (token B, worth $0.80 each) is added to `allowedTokens` via `reinitialize` or `addAllowedToken`.
3. Attacker calls `deposit(tokenB, 1000)` → pays 1000 × $0.80 = $800, receives 1000 `wrsETH`.
4. Attacker calls `withdraw(tokenA, 1000)` → burns 1000 `wrsETH`, receives 1000 × $1.00 = $1000 of canonical rsETH.
5. Net profit: $200. Legitimate depositors of token A can no longer redeem their rsETH from the wrapper. [6](#0-5) [5](#0-4)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L24-24)
```text
    mapping(address allowedToken => bool isAllowed) public allowedTokens;
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L47-49)
```text
    function reinitialize(address _altRsETH) external reinitializer(2) onlyRole(DEFAULT_ADMIN_ROLE) {
        _addAllowedToken(_altRsETH);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L84-86)
```text
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L174-176)
```text
    function addAllowedToken(address _asset) external onlyRole(TIMELOCK_ROLE) {
        _addAllowedToken(_asset);
    }
```
