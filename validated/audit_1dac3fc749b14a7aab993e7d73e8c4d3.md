### Title
Stale zone-B membership cache in vault GetSecrets restriction can permit access to workflows that later become restricted - ([File: core/capabilities/vault/zone_b_restriction.go])

### Summary
The Unlock refund bug is a "stale state used instead of current authoritative state" class of bug: a per-user snapshot (price paid) is missing, so a later mutable value (current price) is substituted, causing incorrect outcomes. The closest analog in this codebase is `zoneBRestrictor` in `core/capabilities/vault/zone_b_restriction.go`, which caches per-`WorkflowDonID` zone-b membership and falls back to that cache instead of the authoritative capabilities registry when the registry lookup fails.

### Finding Description
`zoneBRestrictor.isZoneBWorkflowDON` is meant to authoritatively resolve, on every `GetSecrets` call, whether the calling workflow DON belongs to the `zone-b` family via `z.capabilitiesRegistry.DONByID` [1](#0-0) . When that lookup fails, the code intentionally falls back to `z.zoneCache`, a map keyed by `workflowDonID` that stores the "last successfully-resolved" boolean membership [2](#0-1) , and this cached value is trusted as if it were current: `if cached, ok := z.cachedZoneMembership(workflowDonID); ok { ... return cached, nil }` [3](#0-2) .

This is structurally the same defect as the Unlock refund bug: a security-relevant attribute of an entity (key price / DON zone membership) can change over time on the authoritative source (the lock contract / the capabilities registry), but the enforcement path can end up using an old, cached value instead of re-deriving the current one, because there is no invalidation or versioning tied to the actual state change. If a workflow DON is later added to the `zone-b` family (e.g. an operator reclassifies it as needing owner-allowlist restriction), any node whose local cache still holds `isZoneB=false` from a previous successful resolution will continue to return `false` whenever the registry view is transiently unavailable — which the code itself acknowledges can happen "e.g. not yet synced after startup, or nil mid-update" [4](#0-3) . In that window, `enforce` will skip the `ownerAllowed.AllowErr` gate entirely [5](#0-4) , allowing a non-allowlisted workflow owner's `GetSecrets` call to succeed when it should have been denied.

### Impact Explanation
If exploited during a registry sync gap, a workflow owner that is not on the zone-b allowlist could read vault secrets belonging to/via a zone-b workflow DON, which is exactly the kind of "allowlist bypass" outcome the analysis criteria call out as valid impact. The comment in the code explicitly frames the master gate as "never trust caller-supplied metadata," but the fallback path effectively trusts stale, non-authoritative local state instead of the registry, undermining that guarantee during the (documented as occurring) resync window.

### Likelihood Explanation
This requires (a) a DON's zone-b family membership to change on-chain and (b) a concurrent/subsequent transient unavailability of the local capabilities registry view on the node evaluating the request (explicitly called out by the code comments as a real, expected occurrence at startup or mid-update). Both conditions are plausible in normal operational conditions rather than requiring a compromised peer or operator misconduct, but the window is likely narrow (until the registry resyncs), so likelihood is low-to-medium.

### Recommendation
Do not treat a cache hit as equivalent to an authoritative "not zone-b" result when the intent of the restriction is security-critical. Options analogous to the Unlock fix (snapshot/version the price at time of purchase) here would be: (1) only use the cache to fail *closed* (i.e., default to `isZoneB=true`/restricted on registry lookup failure, not to the last resolved value) so a resync gap cannot silently downgrade a DON that may have just become zone-b, or (2) tie the cache entry to the registry's config/version number and invalidate it whenever the DON's config or `ConfigVersion` changes, so a stale answer is never served across a real membership change.

### Proof of Concept
1. Node resolves DON `X` via `isZoneBWorkflowDON`; registry currently reports `X` is not in `zone-b`; result `false` is cached in `zoneCache[X]` [6](#0-5) .
2. On-chain/off-chain registry update adds DON `X` to the `zone-b` family (a legitimate re-classification).
3. Before the node's local capabilities-registry view resyncs (or during a transient unavailability window, which the code comments confirm can occur), a workflow owner belonging to DON `X` who is NOT on the `VaultZoneBGetSecretsAllowed` allowlist calls `GetSecrets`.
4. `enforce` calls `isZoneBWorkflowDON`, `DONByID` fails/returns stale data, and the cached `false` is returned, so `enforce` returns `nil` without ever calling `z.ownerAllowed.AllowErr(ctx)` [7](#0-6) .
5. The non-allowlisted owner's secret read succeeds despite DON `X` now being a restricted zone-b DON.

Note: I could not fully trace the exact call path from the gateway/HTTP-facing vault `GetSecrets` handler through to `enforce` (e.g., `core/capabilities/vault/capability.go`) within the available iterations, so the precise unprivileged-client trigger point (how `workflowDonID` and owner are derived from an inbound request) is asserted based on the doc comments in `zone_b_restriction.go` rather than fully verified end-to-end. This should be confirmed by reading `core/capabilities/vault/capability.go` in full before treating this as conclusively exploitable end-to-end.

### Citations

**File:** core/capabilities/vault/zone_b_restriction.go (L36-42)
```go
	// zoneCacheMu guards zoneCache.
	zoneCacheMu sync.RWMutex
	// zoneCache holds the last successfully-resolved zone-b membership per
	// WorkflowDonID. It is the fallback when the capabilities registry view is
	// transiently unavailable, so a registry blip does not fail every vault read
	// DON-wide (see isZoneBWorkflowDON).
	zoneCache map[uint32]bool
```

**File:** core/capabilities/vault/zone_b_restriction.go (L71-95)
```go
func (z *zoneBRestrictor) enforce(ctx context.Context, workflowDonID uint32) error {
	enabled, err := z.restrictEnabled.Limit(ctx)
	if err != nil {
		return fmt.Errorf("could not evaluate zone-b vault read restriction gate: %w", err)
	}
	if !enabled {
		return nil
	}

	isZoneB, err := z.isZoneBWorkflowDON(ctx, workflowDonID)
	if err != nil {
		// Fail closed: if we cannot authoritatively resolve the caller's zone, do
		// not proceed. The registry is in-process, so this only fires for an
		// unknown/unregistered WorkflowDonID.
		return err
	}
	if !isZoneB {
		return nil
	}

	if err := z.ownerAllowed.AllowErr(ctx); err != nil {
		return fmt.Errorf("zone-b workflow DON may only read vault secrets for allowlisted workflow owners: %w", err)
	}
	return nil
}
```

**File:** core/capabilities/vault/zone_b_restriction.go (L100-122)
```go
func (z *zoneBRestrictor) isZoneBWorkflowDON(ctx context.Context, workflowDonID uint32) (bool, error) {
	don, err := z.capabilitiesRegistry.DONByID(ctx, workflowDonID)
	if err != nil {
		// The registry view can be transiently unavailable (e.g. not yet synced
		// after startup, or nil mid-update: DONByID returns "metadataRegistry
		// information not available"). That error is not specific to zone-b
		// callers, so failing closed here would block every vault GetSecrets read
		// DON-wide. Fall back to the last successfully-resolved membership for this
		// DON; only a never-before-resolved DON fails closed.
		if cached, ok := z.cachedZoneMembership(workflowDonID); ok {
			z.lggr.Warnw("capabilities registry lookup failed; using cached zone-b membership",
				"workflowDonID", workflowDonID, "isZoneB", cached, "err", err)
			return cached, nil
		}
		return false, fmt.Errorf("could not resolve caller workflow DON %d for zone-b vault read restriction: %w", workflowDonID, err)
	}
	// Case-insensitive match: family casing may vary across registry sources.
	isZoneB := slices.ContainsFunc(don.Families, func(family string) bool {
		return strings.EqualFold(family, zoneBFamily)
	})
	z.storeZoneMembership(workflowDonID, isZoneB)
	return isZoneB, nil
}
```
