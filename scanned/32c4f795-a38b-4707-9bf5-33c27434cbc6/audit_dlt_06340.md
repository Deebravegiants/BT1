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

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Blast-Futures-Exchange-0x97895c329b950755566ddcdad3395caaea395074/issues/23_
