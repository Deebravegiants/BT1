# [M] TrustService::changeEntityOwner can overwrite existing _newOwner record, breaking 1-1 relationship between owners and addresses

## Summary
Severity: Medium
Contest weight: 0.0000
Dataset id: 23425
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability resides in the TrustService contract’s changeEntityOwner function, which updates the mapping that links an entity to its owner without enforcing the invariant that each owner may be associated with only one entity. The root cause is the absence of a check on the _newOwner address before overwriting the internal _newOwner record; the function simply writes the new association, thereby destroying any previous reverse mapping entry for that address. An attacker or any caller with permission to invoke changeEntityOwner can exploit this by selecting a new owner that already controls another entity. The exploit proceeds step‑by‑step: first, two distinct entities are created with separate owners; second, changeEntityOwner is called to transfer one entity to the address that already owns the second entity; third, the contract overwrites the owner‑to‑entity reverse mapping for the new owner, so the forward mapping now shows the new owner as controlling both entities, while the reverse mapping retains only the most recent association. As a result, the previously owned entity becomes orphaned—its owner cannot be retrieved through getEntityByOwner, and the original owner loses any reference to an entity. This breaks the business logic that assumes a one‑to‑one relationship between owners and entities, leading to accounting inconsistencies, potential denial‑of‑service for legitimate owners, and the possibility of hiding or misrepresenting ownership rights. The issue manifests when changeEntityOwner is called with a _newOwner that already has an entry in the owner‑to‑entity map; under those conditions the contract silently corrupts its state. Users experience symptoms such as seeing two entities listed under the same address in the UI while the lookup function returns only one, or finding that an entity they previously owned is no longer reachable, giving the impression that funds or rights have disappeared. The bug was discovered through a targeted unit test that performed the ownership transfer and asserted the expected one‑to‑one mapping, which failed after the transfer. Because the forward mapping still appears correct, the inconsistency can be subtle and may go unnoticed until reverse lookups are performed. The recommended remediation is to enforce uniqueness of the new owner, for example by adding a modifier (onlyNewEntityOwner) or an explicit require statement that checks the reverse mapping is empty before allowing the change, and to update both mappings atomically to preserve the invariant. This conceptual fix restores the intended one‑to‑one relationship and prevents orphaned entities and ambiguous ownership states.

## Proof of Concept
```typescript
it('overwrite existing owner breaks 1-1 relationship', async function() {
const [owner, firstOwner, secondOwner] = await hre.ethers.getSigners();
const { trustService } = await loadFixture(deployDSTokenRegulated);
// Setup: Create two entities with different owners
await trustService.setRole(firstOwner, DSConstants.roles.ISSUER);
await trustService.setRole(secondOwner, DSConstants.roles.ISSUER);
const entity1 = "Entity1";
const entity2 = "Entity2";
const trustServiceFromFirst = await trustService.connect(firstOwner);
await trustServiceFromFirst.addEntity(entity1, firstOwner);
const trustServiceFromSecond = await trustService.connect(secondOwner);
await trustServiceFromSecond.addEntity(entity2, secondOwner);
// Verify initial state
expect(await trustService.getEntityByOwner(firstOwner)).equal(entity1);
expect(await trustService.getEntityByOwner(secondOwner)).equal(entity2);
// Change entity1 owner from firstOwner to secondOwner
await trustService.changeEntityOwner(entity1, firstOwner, secondOwner);
36
// Bug: secondOwner now owns both entities in the forward mapping
// but reverse mapping shows only entity1
expect(await trustService.getEntityByOwner(secondOwner)).equal(entity1);
// entity2 is now orphaned - no way to find its owner through getEntityByOwner
// firstOwner has no entity in reverse mapping
expect(await trustService.getEntityByOwner(firstOwner)).equal("");
});
Run with: npx hardhat test --grep "overwrite existing owner".
```

## Recommendation
Recommended Mitigation: Add modifier onlyNewEntityOwner(_newOwner) to function changeEntityOwner.
