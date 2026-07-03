### Title
Incorrect `_sender` in `Withdraw` Event When `withdrawTo()` Is Called with a Different Recipient - (File: `contracts/agETH/AGETHTokenWrapper.sol`)

---

### Summary

`AGETHTokenWrapper._withdraw()` emits `Withdraw(_asset, _to, _amount)`, passing the recipient `_to` as the `_sender` field. When `withdrawTo(asset, _to, _amount)` is called with `_to != msg.sender`, the event records the wrong address as the initiator of the withdrawal.

---

### Finding Description

The `Withdraw` event in `AGETHTokenWrapper` is declared as:

```solidity
event Withdraw(address asset, address _sender, uint256 _amount);
``` [1](#0-0) 

The internal `_withdraw()` function burns tokens from `msg.sender` and transfers the underlying asset to `_to`, but emits the event with `_to` in the `_sender` position:

```solidity
function _withdraw(address _asset, address _to, uint256 _amount) internal {
    if (!allowedTokens[_asset]) revert TokenNotAllowed();
    _burn(msg.sender, _amount);
    ERC20Upgradeable(_asset).safeTransfer(_to, _amount);
    emit Withdraw(_asset, _to, _amount);   // _to used as _sender — incorrect
}
``` [2](#0-1) 

This is triggered by the public `withdrawTo()` entry point:

```solidity
function withdrawTo(address asset, address _to, uint256 _amount) external {
    _withdraw(asset, _to, _amount);
}
``` [3](#0-2) 

The sibling contract `RsETHTokenWrapper` correctly separates `sender` and `receiver` in its event and emits `msg.sender` as the sender:

```solidity
event Withdraw(address indexed asset, address indexed sender, address indexed receiver, uint256 amount);
// ...
emit Withdraw(_asset, msg.sender, _to, _amount);
``` [4](#0-3) [5](#0-4) 

`AGETHTokenWrapper` never records `msg.sender` in the `Withdraw` event at all — it only records `_to`.

---

### Impact Explanation

Any off-chain system (indexer, analytics dashboard, accounting tool, tax reporter, or protocol-level monitor) that consumes `Withdraw` events to determine who initiated a withdrawal will receive the recipient address instead of the actual initiator. When `_to == msg.sender` (the `withdraw()` path) the bug is invisible; it only manifests on the `withdrawTo()` path. The on-chain token operations themselves are correct — the wrong data is confined to the emitted event. This falls under **Low — contract fails to deliver promised returns**, as the contract's observable interface (its events) does not accurately reflect the actual operation performed.

---

### Likelihood Explanation

`withdrawTo()` is a public, permissionless function callable by any agETH wrapper holder. Any user who calls `withdrawTo()` with a recipient different from themselves triggers the incorrect event. The function requires no special role or privilege. [3](#0-2) 

---

### Recommendation

Change `_withdraw()` to emit `msg.sender` as the sender, not `_to`:

```solidity
emit Withdraw(_asset, msg.sender, _amount);
```

Optionally, align the event signature with `RsETHTokenWrapper` to include both sender and receiver:

```solidity
event Withdraw(address asset, address sender, address receiver, uint256 amount);
// ...
emit Withdraw(_asset, msg.sender, _to, _amount);
``` [2](#0-1) 

---

### Proof of Concept

1. Alice holds 10 agETH wrapper tokens.
2. Alice calls `withdrawTo(altAgETH, bob, 10e18)` — she wants to send the underlying altAgETH to Bob.
3. Inside `_withdraw()`:
   - `_burn(msg.sender, 10e18)` — burns 10 wrapper tokens from Alice. ✓
   - `safeTransfer(bob, 10e18)` — sends 10 altAgETH to Bob. ✓
   - `emit Withdraw(altAgETH, bob, 10e18)` — records **Bob** as `_sender`. ✗
4. Any indexer or off-chain system reading the `Withdraw` event concludes that **Bob** withdrew 10 altAgETH, when in fact **Alice** initiated the withdrawal.
5. Alice's withdrawal activity is invisible in event logs; Bob appears as an initiator of a withdrawal he never requested. [2](#0-1)

### Citations

**File:** contracts/agETH/AGETHTokenWrapper.sol (L32-32)
```text
    event Withdraw(address asset, address _sender, uint256 _amount);
```

**File:** contracts/agETH/AGETHTokenWrapper.sol (L83-85)
```text
    function withdrawTo(address asset, address _to, uint256 _amount) external {
        _withdraw(asset, _to, _amount);
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

**File:** contracts/L2/RsETHTokenWrapper.sol (L35-35)
```text
    event Withdraw(address indexed asset, address indexed sender, address indexed receiver, uint256 amount);
```

**File:** contracts/L2/RsETHTokenWrapper.sol (L127-127)
```text
        emit Withdraw(_asset, msg.sender, _to, _amount);
```
