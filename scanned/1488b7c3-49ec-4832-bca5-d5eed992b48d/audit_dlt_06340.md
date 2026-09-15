# [M] `makeOwnerAdmin()` is not protecting enough from malicious admin act

## Summary
Severity: Medium
Chain: Smart contract
Component: Blast-Futures-Exchange
Published: 2024-02-05
Source: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/23
Type: hats-finding

## Details
**Github username:** @chainNue
**Twitter username:** chainNue
**Submission hash (on-chain):** 0xfd21d26e7cda815dea2f3a9bff19d74a4afcbf4282d5cf28d245dac1ec227cbb
**Severity:** medium

**Description:**
**Description**\

BFX vault have 3 roles, Admin, Trader and Treasurer. 
The Admin users can add and remove roles, this include admin role of the owner.

```js
File: BfxVault.sol
189:     function addRole(address signer, uint256 role) public {
190:         require(signers[msg.sender][ADMIN_ROLE], "NOT_AN_ADMIN");
191:         signers[signer][role] = true;
192:         emit AddRole(signer, role);
193:     }
...
206:     function removeRole(address signer, uint256 role) public {
207:         require(signers[msg.sender][ADMIN_ROLE], "NOT_AN_ADMIN");
208:         signers[signer][role] = false;
209:         emit RemoveRole(signer, role);
210:     }
```

Interestingly, there is `makeOwnerAdmin()` function to restore `owner` to become `admin` (again). Meanwhile, `owner` is immutable (means it will not be changed/transfered), and in constructor this `owner` already set as `admin`, so the existance of this `makeOwnerAdmin()` function raise my assumption, the dev believe there is an edge case possibility a malicious admin can removed the owner as admin.

```js
File: BfxVault.sol
212:     function makeOwnerAdmin() external onlyOwner {
213:         signers[owner][ADMIN_ROLE] = true;
214:     }
```

But, this (makeOwnerAdmin) backup mechanism doesn't really fixed the situation well.

Again, assuming `makeOwnerAdmin()` is to restore owner to be admin again due to malicious other admin act, then, this malicious admin need to be cleared or removed by owner.

Since admin can add other roles, it's possible this malicious admin can assign many address to became admin or any roles. Therefore, owner should manually remove this malicious backup admin. It's like chasing each other between owner and malicious admin, which can involve any front-run mechanics.

The only way to 'fix' this is to pause the `addRole` function, to prevent any further malicious role being added.

**Attack Scenario**\
1. Alice is owner (and admin), Bob, Carol are assigned by Alice as admin
2. Bob turns out act maliciously, and remove Alice, and Carol as Admin
3. Alice gain her admin via `makeOwnerAdmin()`
4. Bob sees Alice gain her admin, thus he now trying to assign other backup address as Admin
5. Alice keep up head to head with Bob, by removing role of Bob's backup address
6. Bob keep front-run Alice by adding more address as Admin, meanwhile he can act maliciously by gaining the Admin role.

Even this issue likelyhood is Low, but the impact and severity is high. Therefore, I assign this a medium one.

**Attachments**

1. **Proof of Concept (PoC) File**
<!-- You must provide a file containing a proof of concept (PoC) that demonstrates the vulnerability you have discovered. -->

1. **Revised Code File (Optional)**
<!-- If possible, please provide a second file containing the revised code that offers a potential fix for the vulnerability. This file should include the following information:
- Comment with a clear explanation of the proposed fix.
- The revised code with your suggested changes.
- Any additional comments or explanations that clarify how the fix addresses the vulnerability. -->

**Recommendation**

Consider to add pausable mechanism on `addRole` which is accessible only by owner
