### Title
ERC-677 `onTokenTransfer` Return Value Not Checked in `transferAndCall` — (File: `contracts/ccip/ERC677.sol`)

---

### Summary

`contracts/ccip/ERC677.sol` implements the ERC-677 `transferAndCall` function but defines `IERC677Receiver.onTokenTransfer` as returning `void` instead of `bool`. As a result, the return value of `onTokenTransfer` is structurally uncapturable and never checked. Any receiver contract that signals rejection by returning `false` from `onTokenTransfer` will have its rejection silently ignored, and the token transfer will be treated as successful. Additionally, the return value of `super.transfer()` is discarded.

---

### Finding Description

In `contracts/ccip/ERC677.sol`, the `IERC677Receiver` interface is declared as:

```solidity
interface IERC677Receiver {
    function onTokenTransfer(address sender, uint256 amount, bytes calldata data) external;
}
```

The ERC-677 proposal specifies that `onTokenTransfer` must return a `bool` indicating success or failure. The interface here declares it as returning nothing (`void`), making it impossible for the caller to ever observe a rejection signal.

The `transferAndCall` implementation then calls:

```solidity
function transferAndCall(address to, uint256 amount, bytes memory data) external returns (bool success) {
    super.transfer(to, amount);          // return value discarded
    emit Transfer(msg.sender, to, amount, data);
    if (to.isContract()) {
        IERC677Receiver(to).onTokenTransfer(msg.sender, amount, data);  // return value structurally absent
    }
    return true;
}
```

Two issues are present:
1. `super.transfer(to, amount)` — the `bool` return value is discarded. (Mitigated in practice because OpenZeppelin ERC20 reverts on failure rather than returning `false`, so no funds are at risk from this specific line.)
2. `IERC677Receiver(to).onTokenTransfer(...)` — because the interface declares the function as returning `void`, the ABI decoder never captures any return data. A receiver that returns `false` to signal rejection is silently ignored; the transfer is finalized regardless.

`WrappedRSETH` inherits directly from `ERC677` and is the live CCIP-compatible wrapped rsETH token deployed on Linea, Optimism, and Zircuit.

---

### Impact Explanation

**Low — Contract fails to deliver promised returns, but doesn't lose value.**

Any user or integrating contract that calls `transferAndCall` on `WrappedRSETH` and relies on the ERC-677 guarantee that a receiver can reject a transfer by returning `false` will find that guarantee is broken. The tokens are unconditionally transferred to the receiver regardless of its `onTokenTransfer` return value. If the receiver contract has no independent mechanism to return the tokens (e.g., it is a contract that only accepts tokens when `onTokenTransfer` succeeds), the tokens may become permanently inaccessible at that address, escalating to a permanent freeze of user funds.

---

### Likelihood Explanation

Low-to-medium. The `transferAndCall` function is publicly callable by any token holder. The impact materializes only when a receiver contract relies on returning `false` from `onTokenTransfer` to reject a transfer. CCIP pool contracts that interact with `WrappedRSETH` are the primary consumers of this path. If any such pool or integrating contract implements the ERC-677 rejection pattern, the broken check silently bypasses it.

---

### Recommendation

1. Update `IERC677Receiver` to declare `onTokenTransfer` as returning `bool`:

```solidity
interface IERC677Receiver {
    function onTokenTransfer(address sender, uint256 amount, bytes calldata data) external returns (bool);
}
```

2. Check the return value in `transferAndCall` and revert on failure:

```solidity
function transferAndCall(address to, uint256 amount, bytes memory data) external returns (bool success) {
    bool transferred = super.transfer(to, amount);
    require(transferred, "ERC677: transfer failed");
    emit Transfer(msg.sender, to, amount, data);
    if (to.isContract()) {
        bool accepted = IERC677Receiver(to).onTokenTransfer(msg.sender, amount, data);
        require(accepted, "ERC677: onTokenTransfer rejected");
    }
    return true;
}
```

---

### Proof of Concept

**Root cause — `IERC677Receiver` declares `void` return:** [1](#0-0) 

**`transferAndCall` discards both return values:** [2](#0-1) 

**`WrappedRSETH` inherits `ERC677` and is the live CCIP token:** [3](#0-2) 

**Attack path:**
1. Attacker (or any user) holds `WrappedRSETH` tokens.
2. Attacker calls `transferAndCall(victimContract, amount, data)` where `victimContract` implements `onTokenTransfer` returning `false` to reject the transfer.
3. `ERC677.transferAndCall` executes `super.transfer`, moving tokens to `victimContract`.
4. `onTokenTransfer` is called; `victimContract` returns `false`.
5. Because the interface declares `void`, the return value is never decoded or checked.
6. `transferAndCall` returns `true`, signalling success.
7. Tokens are now at `victimContract` with no protocol-level mechanism to recover them, as the rejection was silently ignored.

### Citations

**File:** contracts/ccip/ERC677.sol (L7-9)
```text
interface IERC677Receiver {
    function onTokenTransfer(address sender, uint256 amount, bytes calldata data) external;
}
```

**File:** contracts/ccip/ERC677.sol (L28-35)
```text
    function transferAndCall(address to, uint256 amount, bytes memory data) external returns (bool success) {
        super.transfer(to, amount);
        emit Transfer(msg.sender, to, amount, data);
        if (to.isContract()) {
            IERC677Receiver(to).onTokenTransfer(msg.sender, amount, data);
        }
        return true;
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L16-20)
```text
/// @notice An audited ERC677 compatible token contract with burn and minting roles.
/// @dev reference:
/// https://github.com/smartcontractkit/ccip/blob/ccip-develop/contracts/src/v0.8/shared/token/ERC677/BurnMintERC677.sol
/// @dev The total supply can be limited during deployment.
contract WrappedRSETH is IBurnMintERC20, ERC677, IERC165, ERC20Burnable, ConfirmedOwnerWithProposal {
```
