Based on my investigation, the storage layer for the Vault DON uses the raw, non-normalized `Owner` string as the key for metadata/secret lookups, while authorization checks (`validateSecretOwnersMatchAuthorized`) use a case-insensitive comparison. This is analogous to the report's bug class ("multiple addresses for the same entity bypass an address-based check"), since an EVM address has many textually distinct but semantically identical representations (checksummed vs lower-case, with/without `0x` prefix).

### Title
Per-owner secret limit and metadata scoping bypassable via non-canonical owner address casing - ([File: core/services/ocr2/plugins/vault/kvstore.go])

### Summary
The Vault DON's authorization layer normalizes owner addresses for comparison via `vaultutils.NormalizeOwner` [1](#0-0)  when checking that the `Owner` field in a request payload matches the authorized workflow owner [2](#0-1) . However, the storage layer (`KVStore`) keys all metadata and secrets by the *raw*, unnormalized `Owner` string [3](#0-2) [4](#0-3) , and the plugin's per-owner quota check passes `req.Id.Owner` straight through without normalization [5](#0-4) .

### Finding Description
`NormalizeOwner` lower-cases and strips the `0x` prefix so that `0xABC...` and `abc...` are treated as the same owner during authorization/binding checks [6](#0-5) . This mirrors the comment in `capability_test.go` that explicitly tests casing/prefix-equivalent addresses as "the same owner" [7](#0-6) .

But once a request passes the owner-binding check, the raw (still differently-cased) `Owner` string from the request payload is what actually gets persisted and used as the storage/lookup key:
- `KeyFor` builds the secret key directly from `id.Owner` with no normalization: `fmt.Sprintf("%s::%s::%s", id.Owner, namespace, id.Key)` [3](#0-2) .
- `GetMetadata`/`WriteMetadata` key by `metadataPrefix + owner` verbatim [8](#0-7) .
- The per-owner secret-count quota enforcement in the OCR3 plugin calls `store.GetSecretIdentifiersCountForOwner(ctx, req.Id.Owner)` using the raw owner string, not a canonicalized one [5](#0-4) .

Because a single logical owner (one EVM address) has many textually distinct string representations that all pass `NormalizeOwner`-based equality (checksummed vs lower-case vs no-`0x`-prefix — exactly the "multiple addresses, one token" problem from the audit report), a client authorized as one workflow owner can submit requests where the payload's `Owner` field is written in a different casing/format on each call. Since the storage key is derived from the raw, non-normalized string, each distinct casing creates an entirely separate metadata bucket and secret namespace under the KV store, even though the authorization layer treats them as "the same" owner for the purposes of the binding check.

### Impact Explanation
This allows an authorized workflow owner to bypass the `MaxSecretsPerOwner` quota by varying the casing/prefix of the `Owner` field across `CreateSecrets` calls — each distinct textual variant is counted and stored independently (`GetSecretIdentifiersCountForOwner` only sees secrets filed under the exact same string), defeating the intended per-owner resource limit `r.cfg.MaxSecretsPerOwner.Check(...)` [9](#0-8) . It can also cause secrets belonging to "the same" owner to become split across multiple metadata records/keys that `ListSecretIdentifiers`/`GetSecrets`/`DeleteSecrets` — which look up metadata by the exact owner string passed in the request — cannot see consistently, leading to inconsistent enumeration and potential difficulty deleting all of a given owner's secrets (a resource/DoS-adjacent and quota-bypass issue) rather than direct fund loss.

### Likelihood Explanation
Medium: any authorized workflow owner (an already-legitimate, unprivileged actor from the DON's perspective) can trigger this simply by choosing a different valid string encoding of their own address in the request `Owner` field on different calls — no special privileges beyond normal workflow secret write access are required, and `NormalizeOwner`'s own doc comment acknowledges this is a known outstanding gap ("When `VaultOwnerAddressCanonicalizationEnabled` is introduced, normalization at ingress will supersede comparison-site calls here") [10](#0-9) , indicating the storage-layer canonicalization is not yet implemented.

### Recommendation
Canonicalize the `Owner` field once at ingress (immediately after the owner-binding check succeeds, before it is used to build any storage key or passed to `GetSecretIdentifiersCountForOwner`/`WriteMetadata`/`KeyFor`), rather than relying on case-insensitive comparison only at authorization time. This matches the recommendation in the referenced report to whitelist/canonicalize identifiers rather than rely on a per-call equality check.

### Proof of Concept
1. Workflow owner `A` is authorized via the allowlist/JWT path for owner string `0xABCDEF...` (checksummed).
2. Call `CreateSecrets` with `SecretIdentifier.Owner = "0xabcdef..."` (all lower-case) repeatedly. Each call passes `validateSecretOwnersMatchAuthorized` because `NormalizeOwner` treats it as equal to the authorized owner [2](#0-1) .
3. Because `req.Id.Owner` used in `GetSecretIdentifiersCountForOwner` and `KeyFor` is the literal (uncanonicalized) string supplied by the caller, calls using `"0xabcdef..."` and `"ABCDEF..."` (no prefix) and `"0xABCDEF..."` (checksummed) each populate separate `Metadata::<owner>` records in the KV store [8](#0-7) .
4. The `MaxSecretsPerOwner` limit, computed per distinct raw string, is bypassed because the true "owner" (the address) is the same but is fragmented across multiple storage keys.

### Citations

**File:** core/capabilities/vault/vaultutils/owner.go (L1-10)
```go
package vaultutils

import "strings"

// NormalizeOwner lowercases an Ethereum owner address for case-insensitive comparison.
// All comparison sites must use this function. When VaultOwnerAddressCanonicalizationEnabled
// is introduced, normalization at ingress will supersede comparison-site calls here.
func NormalizeOwner(owner string) string {
	return strings.ToLower(strings.TrimPrefix(owner, "0x"))
}
```

**File:** core/capabilities/vault/authorizer.go (L199-215)
```go
func validateEncryptedSecretOwnerMismatch(encryptedSecrets []*vaultcommon.EncryptedSecret, workflowOwner string) error {
	if len(encryptedSecrets) == 0 {
		return errors.New("request batch must contain at least 1 item")
	}
	for idx, encryptedSecret := range encryptedSecrets {
		if encryptedSecret == nil {
			return fmt.Errorf("encrypted secret must not be nil at index %d", idx)
		}
		if encryptedSecret.Id == nil {
			return fmt.Errorf("secret ID must not be nil at index %d", idx)
		}
		if vaultutils.NormalizeOwner(encryptedSecret.Id.Owner) != vaultutils.NormalizeOwner(workflowOwner) {
			return fmt.Errorf("encrypted secret owner at index %d %q does not match authorized workflow owner %q", idx, encryptedSecret.Id.Owner, workflowOwner)
		}
	}
	return nil
}
```

**File:** core/capabilities/vault/vaulttypes/types.go (L90-93)
```go
func KeyFor(id *vaultcommon.SecretIdentifier) string {
	namespace := NormalizeNamespace(id.Namespace)
	return fmt.Sprintf("%s::%s::%s", id.Owner, namespace, id.Key)
}
```

**File:** core/services/ocr2/plugins/vault/kvstore.go (L89-138)
```go
func (s *KVStore) GetMetadata(ctx context.Context, owner string) (*vault.StoredMetadata, error) {
	defer s.trackDuration(ctx, "GetMetadata", time.Now())
	b, err := s.reader.Read([]byte(metadataPrefix + owner))
	if err != nil {
		return nil, fmt.Errorf("failed to read metadata: %w", err)
	}

	if b == nil {
		return nil, nil
	}

	md := &vault.StoredMetadata{}
	err = proto.Unmarshal(b, md)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal md: %w", err)
	}
	return md, nil
}

func (s *KVStore) GetSecretIdentifiersCountForOwner(ctx context.Context, owner string) (int, error) {
	defer s.trackDuration(ctx, "GetSecretIdentifiersCountForOwner", time.Now())
	md, err := s.GetMetadata(ctx, owner)
	if err != nil {
		return 0, fmt.Errorf("failed to get metadata for owner %s: %w", owner, err)
	}

	count := 0
	if md != nil {
		count = len(md.SecretIdentifiers)
	}
	return count, nil
}

func (s *KVStore) WriteMetadata(ctx context.Context, owner string, metadata *vault.StoredMetadata) error {
	defer s.trackDuration(ctx, "WriteMetadata", time.Now())
	if metadata == nil {
		return errors.New("metadata cannot be nil")
	}
	b, err := proto.Marshal(metadata)
	if err != nil {
		return fmt.Errorf("failed to marshal metadata: %w", err)
	}

	err = s.writer.Write([]byte(metadataPrefix+owner), b)
	if err != nil {
		return fmt.Errorf("failed to write metadata: %w", err)
	}

	return nil
}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L2052-2064)
```go
	count, err := store.GetSecretIdentifiersCountForOwner(ctx, req.Id.Owner)
	if err != nil {
		return nil, fmt.Errorf("failed to read secret identifiers count for owner: %w", err)
	}

	// TODO orgID https://smartcontract-it.atlassian.net/browse/CRE-1707
	ctx = contexts.WithCRE(ctx, contexts.CRE{Owner: req.Id.Owner})
	if ierr := r.cfg.MaxSecretsPerOwner.Check(ctx, count+1); ierr != nil {
		if errBoundLimited, ok := errors.AsType[limits.ErrorBoundLimited[int]](ierr); ok {
			return nil, vaulttypes.NewUserError(fmt.Sprintf("could not write to key value store: owner %s has reached maximum number of secrets (limit=%d)", req.Id.Owner, errBoundLimited.Limit))
		}
		return nil, fmt.Errorf("failed to check max secrets per owner limit: %w", ierr)
	}
```

**File:** core/capabilities/vault/capability_test.go (L405-428)
```go
		{
			name:          "matching with different casing",
			workflowOwner: "0xABCDEF1234567890ABCDEF1234567890ABCDEF12",
			secretOwners:  []string{"0xabcdef1234567890abcdef1234567890abcdef12"},
			shouldReject:  false,
		},
		{
			name:          "matching with 0x prefix vs without",
			workflowOwner: "0xabcdef1234567890abcdef1234567890abcdef12",
			secretOwners:  []string{"abcdef1234567890abcdef1234567890abcdef12"},
			shouldReject:  false,
		},
		{
			name:          "matching without 0x prefix vs with",
			workflowOwner: "abcdef1234567890abcdef1234567890abcdef12",
			secretOwners:  []string{"0xabcdef1234567890abcdef1234567890abcdef12"},
			shouldReject:  false,
		},
		{
			name:          "matching with mixed casing and prefix difference",
			workflowOwner: "0xAbCdEf1234567890AbCdEf1234567890AbCdEf12",
			secretOwners:  []string{"abcdef1234567890abcdef1234567890abcdef12"},
			shouldReject:  false,
		},
```
