# [H] TrustService::removeRole doesn't delete already owned entities so address which lost role can still manage existing entities

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23424
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability is an incomplete cleanup of entity ownership data when an address’s role is removed in the TrustService contract. The removeRole function only updates the role mapping to NONE but fails to delete or reset the ownersEntities mapping and the associated operator and resource mappings that link the address to previously created entities. Because the onlyEntityOwnerOrAbove modifier checks both the role and the ownersEntities mapping, the stale ownership entry allows the address to continue passing the access‑control check even after its role has been revoked. An attacker who previously held the ISSUER role can therefore still add operators, add resources, or otherwise manage the entity, effectively retaining privileged control despite appearing to have no role. This can be exploited by first creating an entity while holding a privileged role, then having the role removed (either voluntarily or by an admin), and finally invoking any function guarded by the entity‑owner modifier; the contract will incorrectly treat the caller as an authorized owner because the ownership mapping was never cleared. The impact includes unauthorized modification of entity metadata, potential redirection of funds or governance rights, and a breach of the protocol’s trust model. The bug manifests whenever a role is revoked after an entity has been created, affecting any address that loses its role but still has lingering ownership entries, as well as the broader protocol that assumes role revocation fully removes access. It was discovered through a targeted unit test that exercised the removal of the ISSUER role and then queried the entity‑owner, operator, and resource look‑ups, observing that the mappings still returned the original entity name and that privileged calls did not revert. The issue is subtle because the role value correctly reports NONE, giving the impression that access is revoked, while the hidden ownership mapping continues to grant authority, making it easy to miss without explicit post‑revocation checks. The proper mitigation is to extend removeRole so that it iterates over or otherwise clears all entity‑ownership, operator, and resource mappings associated with the address, ensuring that no stale references remain and that the onlyEntityOwnerOrAbove modifier cannot be satisfied after role removal. This class of bug belongs to the broader category of access‑control state‑inconsistency where role revocation does not fully purge related permission data, leading to orphaned privileges and potential security breaches.

## Proof of Concept
```typescript
// Add PoC to test/trust-service.test.ts:
it('Should demonstrate orphaned entity relationships after role removal', async function() {
  const [owner, entityOwner, operator, resource] = await hre.ethers.getSigners();
  const { trustService } = await loadFixture(deployDSTokenRegulated);
  // Step 1: Give entityOwner ISSUER role
  await trustService.setRole(entityOwner, DSConstants.roles.ISSUER);
  expect(await trustService.getRole(entityOwner)).equal(DSConstants.roles.ISSUER);
  // Step 2: Create an entity owned by entityOwner
  const entityName = "TestEntity";
  const trustServiceFromEntityOwner = await trustService.connect(entityOwner);
  await trustServiceFromEntityOwner.addEntity(entityName, entityOwner);
  // Verify entity ownership
  expect(await trustService.getEntityByOwner(entityOwner)).equal(entityName);
  // Step 3: Add operator and resource to the entity
  await trustServiceFromEntityOwner.addOperator(entityName, operator);
  await trustServiceFromEntityOwner.addResource(entityName, resource);
  // Verify operator and resource are linked to entity
  expect(await trustService.getEntityByOperator(operator)).equal(entityName);
  expect(await trustService.getEntityByResource(resource)).equal(entityName);
  // Step 4: Remove entityOwner's ISSUER role
  await trustService.removeRole(entityOwner);
  expect(await trustService.getRole(entityOwner)).equal(DSConstants.roles.NONE);
  // Step 5: Demonstrate the bug - entity relationships still exist
  // These should ideally be cleaned up but they're not:
  expect(await trustService.getEntityByOwner(entityOwner)).equal(entityName); // Still owns entity!
  expect(await trustService.getEntityByOperator(operator)).equal(entityName); // Still linked!
  expect(await trustService.getEntityByResource(resource)).equal(entityName); // Still linked!
  // Step 6: Show the security issue - entityOwner can still manage the entity
  // even without any role
  await expect(
    trustServiceFromEntityOwner.addOperator(entityName, hre.ethers.Wallet.createRandom())
  ).to.not.be.reverted; // This should fail but doesn't!
  // The onlyEntityOwnerOrAbove modifier still passes because:
  // - entityOwner has NONE role (not MASTER/ISSUER)
  // - But ownersEntities[entityOwner] still equals entityName
  // - So the check passes even though they shouldn't have access
});
```

## Recommendation
When an address loses its role, delete entities it previously owned by clearing the entity ownership mappings.
