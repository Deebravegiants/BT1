### Title
`increaseApproval` Returns Nothing While `decreaseApproval` Returns `bool`, Breaking Return-Type Symmetry — (`contracts/ccip/WrappedRSETH.sol`)

---

### Summary

`WrappedRSETH` exposes two backwards-compatibility helpers, `increaseApproval` and `decreaseApproval`. `decreaseApproval` returns `bool success`, but `increaseApproval` is declared `void`. Any caller that treats the two functions as symmetric — expecting a `bool` from `increaseApproval` — will silently receive zero return bytes.

---

### Finding Description

In `contracts/ccip/WrappedRSETH.sol`, the two backwards-compatibility wrappers are declared as:

```solidity
// line 89
function decreaseApproval(address spender, uint256 subtractedValue) external returns (bool success) {
    return decreaseAllowance(spender, subtractedValue);
}

// line 94
function increaseApproval(address spender, uint256 addedValue) external {   // ← no return value
    increaseAllowance(spender, addedValue);
}
``` [1](#0-0) 

The underlying `increaseAllowance` (inherited from OpenZeppelin ERC20) **does** return `bool`:

```solidity
function increaseAllowance(address spender, uint256 addedValue) public virtual returns (bool) { ... }
``` [2](#0-1) 

The wrapper discards that return value and exposes a `void` signature, while the analogous `decreaseApproval` correctly propagates `bool`. The comment on both functions states they "exist to be backwards compatible with the older naming convention," implying they should behave identically in terms of ABI shape.

---

### Impact Explanation

No funds are lost and no allowance is set incorrectly — `increaseAllowance` still executes and updates state. The impact is purely at the ABI/integration layer:

- An off-chain script or integrator contract that calls `increaseApproval` via a low-level `call` and attempts to ABI-decode the return bytes as `bool` will receive **0 bytes**, which decodes to `false` (or reverts with a strict ABI decoder), potentially causing downstream approval-dependent logic to be skipped.
- `decreaseApproval` returns 32 bytes (`true`), so the two functions are not drop-in symmetric despite the identical intent stated in their NatSpec.

This matches the allowed scope: **Low — Contract fails to deliver promised returns, but doesn't lose value.**

---

### Likelihood Explanation

Any integrator or off-chain tooling that mirrors the `decreaseApproval` calling pattern against `increaseApproval` and inspects the return value will be affected. The CCIP bridge ecosystem commonly uses low-level calls with return-value checks for token interactions, making this a realistic integration hazard.

---

### Recommendation

Add a `bool` return type to `increaseApproval` and propagate the return value from `increaseAllowance`:

```solidity
function increaseApproval(address spender, uint256 addedValue) external returns (bool) {
    return increaseAllowance(spender, addedValue);
}
```

This mirrors the existing `decreaseApproval` implementation exactly.

---

### Proof of Concept

```solidity
// Local fork / unit test — no mainnet interaction
function testReturnAsymmetry() public {
    address spender = address(0xBEEF);
    uint256 amount  = 1e18;

    // increaseApproval — expect bool but get 0 bytes
    (bool ok1, bytes memory ret1) = address(token).call(
        abi.encodeWithSignature("increaseApproval(address,uint256)", spender, amount)
    );
    assert(ok1);
    assert(ret1.length == 0);          // ← no return data

    // decreaseApproval — returns bool true (32 bytes)
    (bool ok2, bytes memory ret2) = address(token).call(
        abi.encodeWithSignature("decreaseApproval(address,uint256)", spender, amount)
    );
    assert(ok2);
    assert(ret2.length == 32);         // ← 32-byte bool
    bool result = abi.decode(ret2, (bool));
    assert(result == true);

    // Asymmetry demonstrated: ret1.length (0) != ret2.length (32)
}
``` [3](#0-2)

### Citations

**File:** contracts/ccip/WrappedRSETH.sol (L88-96)
```text
    /// @dev Exists to be backwards compatible with the older naming convention.
    function decreaseApproval(address spender, uint256 subtractedValue) external returns (bool success) {
        return decreaseAllowance(spender, subtractedValue);
    }

    /// @dev Exists to be backwards compatible with the older naming convention.
    function increaseApproval(address spender, uint256 addedValue) external {
        increaseAllowance(spender, addedValue);
    }
```

**File:** lib/openzeppelin-contracts/contracts/token/ERC20/ERC20.sol (L177-181)
```text
    function increaseAllowance(address spender, uint256 addedValue) public virtual returns (bool) {
        address owner = _msgSender();
        _approve(owner, spender, allowance(owner, spender) + addedValue);
        return true;
    }
```
