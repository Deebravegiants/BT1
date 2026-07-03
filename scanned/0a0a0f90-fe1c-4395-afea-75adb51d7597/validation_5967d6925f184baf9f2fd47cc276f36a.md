### Title
Unprivileged Users Can Drain `RsETHTokenWrapper` by Depositing a Discounted Allowed Token and Withdrawing a More Valuable One at 1:1 - (File: contracts/L2/RsETHTokenWrapper.sol)

### Summary
`RsETHTokenWrapper` supports multiple allowed tokens (all treated as 1:1 equivalent to wrsETH) but performs no value-equivalence check at deposit or withdrawal time. Any unprivileged user can deposit a lower-value allowed rsETH variant and immediately withdraw a higher-value allowed rsETH variant at the same nominal amount, draining the wrapper of the more valuable token.

### Finding Description
`RsETHTokenWrapper` is designed to wrap "alternative rsETH tokens" from different L2 bridging paths into a single canonical `wrsETH`. The contract explicitly supports multiple allowed tokens: the `initialize` function registers the first token, `reinitialize` adds a second, and `addAllowedToken` (TIMELOCK_ROLE) can add more.

The public `deposit` and `withdraw` functions (and their `depositTo`/`withdrawTo` variants) are callable by any address with no access restriction:

```solidity
function deposit(address asset, uint256 _amount) external {
    _deposit(asset, msg.sender, _amount);
}
function withdraw(address asset, uint256 _amount) external {
    _withdraw(asset, msg.sender, _amount);
}
```

`_deposit` mints wrsETH 1:1 for any allowed token:
```solidity
function _deposit(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);
    _mint(_to, _amount);
}
```

`_withdraw` burns wrsETH and transfers any allowed token 1:1:
```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
}
```

There is no check that the deposited token and the withdrawn token have the same market value. The contract assumes all allowed tokens are perpetually equivalent, but bridged rsETH variants can and do trade at different prices (e.g., due to bridge liquidity constraints, bridge-specific risk premiums, or temporary depegs).

### Impact Explanation
**Critical — Direct theft of user funds.**

An attacker who holds a discounted rsETH variant (e.g., rsETH bridged via a less-trusted path, trading at 0.98 ETH) can:
1. Deposit N units of the discounted token → receive N wrsETH.
2. Immediately withdraw N units of the canonical/more-valuable rsETH variant (e.g., trading at 1.00 ETH) → burn N wrsETH.

The attacker profits the price spread on N tokens. The loss is borne by other users whose canonical rsETH deposits are now replaced by the discounted variant in the wrapper's balance. Repeated at scale, the wrapper can be fully drained of its most valuable token.

### Likelihood Explanation
**Medium.**

Multiple allowed tokens is the explicit, intended design — `reinitialize` adds a second token and `addAllowedToken` supports further additions. Price discrepancies between bridged rsETH variants are realistic: different bridges carry different risk premiums, liquidity depths, and withdrawal delays. Secondary-market price differences of even 0.1–2% are sufficient to make the attack profitable. No special role or privileged access is required; any holder of the discounted variant can execute this atomically.

### Recommendation
1. **Enforce single-token semantics**: If the wrapper is intended to hold only one canonical rsETH variant at a time, remove multi-token support or enforce that only one token can have a non-zero balance.
2. **Add value-equivalence checks**: Before allowing a withdrawal of token B after a deposit of token A, verify via an on-chain oracle that both tokens are within an acceptable price band of each other.
3. **Track per-token balances against per-token minted supply**: Ensure that the amount of wrsETH redeemable for token X cannot exceed the amount of token X that was deposited, preventing cross-token arbitrage.

### Proof of Concept
Preconditions: `allowedTokens[rsETH_v1] = true`, `allowedTokens[rsETH_v2] = true`. Market price: rsETH_v1 = 0.97 ETH, rsETH_v2 = 1.00 ETH. Wrapper holds 1000 rsETH_v2 deposited by honest users.

1. Attacker buys 1000 rsETH_v1 on secondary market for 970 ETH.
2. Attacker calls `deposit(rsETH_v1, 1000e18)` → receives 1000 wrsETH. [1](#0-0) 
3. Attacker calls `withdraw(rsETH_v2, 1000e18)` → burns 1000 wrsETH, receives 1000 rsETH_v2 worth 1000 ETH. [2](#0-1) 
4. Attacker sells 1000 rsETH_v2 for 1000 ETH, netting ~30 ETH profit.
5. Honest users who deposited rsETH_v2 now hold claims only against rsETH_v1 (worth 970 ETH), a direct loss of ~30 ETH.

The root cause — no value check between deposited and withdrawn token — is entirely within `RsETHTokenWrapper._deposit` and `_withdraw`. [3](#0-2)

### Citations

**File:** contracts/L2/RsETHTokenWrapper.sol (L69-71)
```text
    function deposit(address asset, uint256 _amount) external {
        _deposit(asset, msg.sender, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L84-86)
```text
    function withdraw(address asset, uint256 _amount) external {
        _withdraw(asset, msg.sender, _amount);
    }
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L120-141)
```text
    function _withdraw(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        _burn(msg.sender, _amount);

        ERC20Upgradeable(_asset).safeTransfer(_to, _amount);

        emit Withdraw(_asset, msg.sender, _to, _amount);
    }

    /// @notice Deposit tokens into the lockbox
    /// @param _asset The address of the token to deposit
    /// @param _to The address to send the XERC20 to
    /// @param _amount The amount of tokens to deposit
    function _deposit(address _asset, address _to, uint256 _amount) internal {
        if (!allowedTokens[_asset]) revert TokenNotAllowed();

        ERC20Upgradeable(_asset).safeTransferFrom(msg.sender, address(this), _amount);

        _mint(_to, _amount);
        emit Deposit(_asset, msg.sender, _to, _amount);
    }
```
