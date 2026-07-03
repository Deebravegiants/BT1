Audit Report

## Title
`burn(address, uint256)` Delegates to `burnFrom` Causing Allowance Revert in CCIP Bridge Flow - (`contracts/ccip/WrappedRSETH.sol`)

## Summary
`burn(address account, uint256 amount)` at line 122 has no `onlyBurner` modifier and unconditionally delegates to `burnFrom`, which calls OZ's `ERC20Burnable.burnFrom`. OZ's implementation requires the caller to hold an ERC-20 allowance from `account` before burning. Because the CCIP token pool (a registered burner) never receives such an allowance from users, every L2-to-L1 burn attempt reverts, blocking the bridge flow for all users who have not manually pre-approved the pool.

## Finding Description
The confirmed call chain when the CCIP pool calls `burn(user, amount)`:

1. `burn(address account, uint256 amount)` — [1](#0-0)  no `onlyBurner` guard, forwards directly to `burnFrom(account, amount)`.
2. `burnFrom(address account, uint256 amount)` — [2](#0-1)  `onlyBurner` passes for the pool, then calls `super.burnFrom(account, amount)`.
3. OZ's `ERC20Burnable.burnFrom` — [3](#0-2)  calls `_spendAllowance(account, _msgSender(), amount)` **before** `_burn`, requiring `account` (the user) to have approved `_msgSender()` (the pool) for at least `amount`.

In the standard CCIP lock-or-burn flow, the pool calls `burn(user, amount)` directly — no user approval of the pool exists. The `onlyBurner` role is intended to be the sole authorization gate, but the delegation to `super.burnFrom` introduces a second, unsatisfied requirement. The fix is to have `burn(address, uint256)` call `_burn(account, amount)` directly under `onlyBurner`, matching the Chainlink reference `BurnMintERC677` design.

## Impact Explanation
Every L2-to-L1 CCIP bridge transfer requires the token pool to call `burn(user, amount)`. This call always reverts for any user who has not manually pre-approved the pool — which is every user under normal operation. Tokens remain accessible on L2 but cannot be bridged back to L1 through the standard CCIP UX. This constitutes **Medium — Temporary freezing of funds**.

## Likelihood Explanation
No attacker is required. The failure is structural and deterministic: it triggers on every single L2-to-L1 bridge attempt by any user. The precondition (no prior `approve(pool, amount)`) is the default state for all users. The workaround (manual out-of-band approval) is not part of the standard CCIP UX and is unknown to typical users.

## Recommendation
Replace the `burn(address, uint256)` → `burnFrom` delegation with a direct `_burn` call guarded by `onlyBurner`:

```solidity
function burn(address account, uint256 amount)
    public
    virtual
    override
    onlyBurner
{
    _burn(account, amount);
}
```

This removes the spurious allowance requirement while preserving the role-based access control.

## Proof of Concept
The submitted Foundry test is valid and directly reproducible against the unmodified contract:

- `test_ccipBurnRevertsWithoutAllowance`: pool calls `burn(user, 1 ether)` without prior approval → reverts with `ERC20InsufficientAllowance`. Confirms bridge is broken.
- `test_ccipBurnSucceedsOnlyWithPriorApproval`: user calls `approve(pool, 1 ether)` first → burn succeeds. Confirms the out-of-band workaround, which is not part of normal CCIP UX.

Both tests exercise only public contract calls available to any bridge user, with no privileged preconditions beyond the pool holding the burner role (which is the intended deployment state).

### Citations

**File:** contracts/ccip/WrappedRSETH.sol (L122-124)
```text
    function burn(address account, uint256 amount) public virtual override {
        burnFrom(account, amount);
    }
```

**File:** contracts/ccip/WrappedRSETH.sol (L129-131)
```text
    function burnFrom(address account, uint256 amount) public override(IBurnMintERC20, ERC20Burnable) onlyBurner {
        super.burnFrom(account, amount);
    }
```

**File:** lib/openzeppelin-contracts/contracts/token/ERC20/extensions/ERC20Burnable.sol (L35-38)
```text
    function burnFrom(address account, uint256 amount) public virtual {
        _spendAllowance(account, _msgSender(), amount);
        _burn(account, amount);
    }
```
