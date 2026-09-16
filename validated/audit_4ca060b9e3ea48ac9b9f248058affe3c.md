## Analog Vulnerability Found

### Title
Unrestricted `superApprove()` grants unlimited ERC20 allowance over any account's tokens - (File: evm/src/utils/HyperFungibleTokenImpl.sol)

### Summary
`HyperFungibleTokenImpl.superApprove(address owner, address spender)` is a `public` function with no access control that lets **any caller** set a `type(uint256).max` ERC20 allowance from an arbitrary `owner` to an arbitrary `spender`. This is the same bug class as the referenced `HopFacetOptimized.setApprovalForBridges()` finding: a permissionless entry point that grants maximum approval, which any attacker can weaponize to drain another account's token balance.

### Finding Description [1](#0-0) 

```solidity
/**
 * @notice Helper function for tests - approves unlimited tokens
 * @param owner The owner of the tokens
 * @param spender The spender address
 */
function superApprove(address owner, address spender) public {
    _approve(owner, spender, type(uint256).max);
}
```

There is no `msg.sender == owner` check, no role check (unlike `mint`/`burn`/`grantMinterRole` in the same contract which are correctly gated with `onlyRole`), and no restriction on `spender`. Any account can call `superApprove(victim, attacker)` to grant `attacker` a `type(uint256).max` allowance over `victim`'s balance in this token, after which `attacker` can call `transferFrom(victim, attacker, balance)` to steal the entire balance.

This contract is not confined to the test suite — it is wired into deployment tooling and a faucet contract, i.e., it is a real deployable token contract: [2](#0-1) 
It is referenced by `evm/script/DeployIsmp.s.sol` and `evm/src/utils/TokenFaucet.sol` (production/testnet deployment paths), not only by test files such as `evm/tests/foundry/FeeToken.sol` and `evm/tests/foundry/BaseTest.sol`.

### Impact Explanation
Any address holding a balance of a deployed `HyperFungibleTokenImpl` instance can have its entire balance drained by an unprivileged attacker: the attacker calls `superApprove(victim, attacker)` then `transferFrom`. This is a direct token-theft primitive reachable from a single unprivileged transaction, matching the "concrete theft of funds" impact bar.

### Likelihood Explanation
High — the function is `public`, requires no special role, no signature, and no prior relationship with the victim. Exploitation is a two-transaction sequence (`superApprove` then `transferFrom`) executable by anyone against any holder of the token, as soon as the contract is deployed with real value.

### Recommendation
Remove `superApprove` entirely from production code (it is explicitly documented as a test helper), or if it must remain for testing, restrict it to `onlyRole(DEFAULT_ADMIN_ROLE)`/a test-only mock contract that is never referenced by deployment scripts, mirroring the `LibDiamond.enforceIsContractOwner()` fix applied to `HopFacetOptimized.setApprovalForBridges()`. At minimum, gate the call with `require(msg.sender == owner)` so a caller can only approve on their own behalf.

### Proof of Concept
```solidity
// Attacker has no special privileges.
HyperFungibleTokenImpl token = HyperFungibleTokenImpl(tokenAddress);
address victim = <any holder>;

vm.prank(attacker);
token.superApprove(victim, attacker); // sets allowance[victim][attacker] = type(uint256).max

vm.prank(attacker);
token.transferFrom(victim, attacker, token.balanceOf(victim)); // drains victim's entire balance
```

### Citations

**File:** evm/src/utils/HyperFungibleTokenImpl.sol (L110-117)
```text
    /**
     * @notice Helper function for tests - approves unlimited tokens
     * @param owner The owner of the tokens
     * @param spender The spender address
     */
    function superApprove(address owner, address spender) public {
        _approve(owner, spender, type(uint256).max);
    }
```

**File:** evm/src/utils/TokenFaucet.sol (L1-1)
```text
// Copyright (C) Polytope Labs Ltd.
```
