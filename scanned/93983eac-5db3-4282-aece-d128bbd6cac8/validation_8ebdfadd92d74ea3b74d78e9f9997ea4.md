Based on my analysis, I found a strong analog to CVE-2024-0551 in this codebase.

### Title
Sensitive DKG key material export accessible via default `Edit` role instead of `Admin` role - (File: core/web/router.go)

### Summary
The `/v2/vault/dkg_results/export` endpoint returns the full DKG result package (containing encrypted TDH2 key share material used by the Vault OCR plugin to derive the node's private key share) to any authenticated user holding the `Edit` role, whereas every other secret/key-export endpoint in the node's API (ETH, OCR, OCR2, P2P, CSA, VRF, and all per-chain keys) is gated behind `RequiresAdminRole`.

### Finding Description
The router wires up the vault export route with a lower-privilege guard than all analogous key-export routes: [1](#0-0) 

Compare this to every other `.../export/...` route in the same file, which uses `auth.RequiresAdminRole`, e.g.: [2](#0-1) [3](#0-2) 

The `RequiresEditRole` middleware only excludes `UserRoleView` and `UserRoleRun`, so any `Edit`-role user (a non-admin, non-owner role) passes: [4](#0-3) 

The handler itself decodes the request, looks up the stored `ReportWithResultPackage` by `instanceId`, and returns it hex-encoded in the response body with no additional authorization check: [5](#0-4) 

This `ReportWithResultPackage` is exactly the material from which the node derives its TDH2 public key and, critically, its private key share (`TDH2PrivateShareFromDKGResult`) used to decrypt vault secrets: [6](#0-5) 

The `dkg_results` table stores this material keyed only by `instance_id`, a value that is not scoped per-user and can be enumerated/guessed by any authenticated party since there is no ownership check in `ReadResultPackage`: [7](#0-6) [8](#0-7) 

This mirrors the CVE-2024-0551 bug class: a data-export capability that discloses sensitive backend material was left reachable at a role level below what its sensitivity warrants (there, default user role vs. required admin privilege for DB export; here, `Edit` role vs. the `Admin` role used for every comparable key-export endpoint in this codebase).

### Impact Explanation
An `Edit`-role user — a role explicitly intended to be less privileged than `Admin` and used for routine job/bridge management — can retrieve the raw hex-encoded DKG result package for any `instanceId` it can guess or observe. This package is the basis for deriving the node's TDH2 private key share used by the Vault capability to decrypt secrets submitted through the vault/workflow system. Exposure of this material to a non-admin actor undermines the confidentiality guarantees of the Vault plugin's threshold decryption scheme and could enable decryption of protected secrets if enough shares (from colluding low-privilege users across the DON, or leaked via this endpoint) are gathered.

### Likelihood Explanation
Exploitation only requires an existing `Edit`-role API/session token (a role routinely granted for job and bridge configuration, not owner/admin-level trust) and knowledge or guessing of a valid `instanceId`, which is not high entropy nor access-controlled at the ORM layer. No additional network position, code execution, or admin credentials are required, making this trivially reachable once minimal privileges are granted — consistent with the "attacker must have been granted access to the system prior to the attack" precondition in the referenced CVE.

### Recommendation
Change the route guard for `/v2/vault/dkg_results/export` (and consider `/vault/dkg_results/verify` if it also discloses meaningful information) from `auth.RequiresEditRole` to `auth.RequiresAdminRole`, consistent with every other key/secret export endpoint registered in `core/web/router.go`. Additionally, consider adding an explicit ownership/ACL check in `ReadResultPackage` rather than relying solely on route middleware.

### Proof of Concept
1. Provision or obtain an API token for a user with role `Edit` (e.g., via `POST /v2/users` by an admin, or an OIDC/LDAP group mapped to `EditClaim`/`EditUserGroupCN`).
2. Authenticate as that user and send:
   ```
   POST /v2/vault/dkg_results/export
   Content-Type: application/json

   {"instanceId": "<known-or-guessed-instance-id>"}
   ```
3. The response returns `hexDKGResultPackage` and its SHA-256, as shown in the passing test `TestVaultController_ExportDKGResult`, which exercises this exact endpoint without asserting any admin-only restriction: [9](#0-8)

### Citations

**File:** core/web/router.go (L313-320)
```go
		authv2.POST("/keys/csa/export/:ID", auth.RequiresAdminRole(csakc.Export))

		ekc := NewETHKeysController(app)
		authv2.GET("/keys/eth", ekc.Index)
		authv2.POST("/keys/eth", auth.RequiresEditRole(ekc.Create))
		authv2.DELETE("/keys/eth/:keyID", auth.RequiresAdminRole(ekc.Delete))
		authv2.POST("/keys/eth/import", auth.RequiresAdminRole(ekc.Import))
		authv2.POST("/keys/eth/export/:address", auth.RequiresAdminRole(ekc.Export))
```

**File:** core/web/router.go (L378-383)
```go
		vrfkc := VRFKeysController{app}
		authv2.GET("/keys/vrf", vrfkc.Index)
		authv2.POST("/keys/vrf", auth.RequiresEditRole(vrfkc.Create))
		authv2.DELETE("/keys/vrf/:keyID", auth.RequiresAdminRole(vrfkc.Delete))
		authv2.POST("/keys/vrf/import", auth.RequiresAdminRole(vrfkc.Import))
		authv2.POST("/keys/vrf/export/:keyID", auth.RequiresAdminRole(vrfkc.Export))
```

**File:** core/web/router.go (L441-443)
```go
		vault := VaultController{app}
		authv2.POST("/vault/dkg_results/verify", auth.RequiresEditRole(vault.VerifyDKGResult))
		authv2.POST("/vault/dkg_results/export", auth.RequiresEditRole(vault.ExportDKGResult))
```

**File:** core/web/auth/auth.go (L217-234)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}
```

**File:** core/web/vault_controller.go (L89-120)
```go
// ExportDKGResult returns the DKGResult corresponding to the given instance ID
// "POST <application>/vault/dkg_results/export"
func (vc *VaultController) ExportDKGResult(c *gin.Context) {
	var req ExportDKGResultRequest
	err := json.NewDecoder(c.Request.Body).Decode(&req)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, errors.New("could not parse request body"))
		return
	}

	if req.InstanceID == "" {
		jsonAPIError(c, http.StatusBadRequest, errors.New("instanceId is required"))
		return
	}

	orm := vault.NewVaultORM(vc.App.GetDB())
	v, err := orm.ReadResultPackage(c.Request.Context(), dkgocrtypes.InstanceID(req.InstanceID))
	if err != nil {
		jsonAPIError(c, http.StatusNotFound, err)
		return
	}

	if v == nil {
		jsonAPIError(c, http.StatusNotFound, errors.New("DKG result not found"))
		return
	}

	hexPackage := hex.EncodeToString(v.ReportWithResultPackage)
	sha := sha256.Sum256(v.ReportWithResultPackage)
	shaStr := hex.EncodeToString(sha[:])
	jsonAPIResponse(c, presenters.NewExportDKGResultResource(hexPackage, shaStr), "exportDKGResult")
}
```

**File:** core/services/ocr2/plugins/vault/plugin.go (L114-147)
```go
func (r *ReportingPluginFactory) getKeyMaterial(ctx context.Context, instanceID string) (publicKey *tdh2easy.PublicKey, privateKeyShare *tdh2easy.PrivateShare, err error) {
	pack, err := r.db.ReadResultPackage(ctx, dkgocrtypes.InstanceID(instanceID))
	if err != nil {
		return nil, nil, fmt.Errorf("could not read result package from db: %w", err)
	}
	if pack == nil {
		return nil, nil, fmt.Errorf("no result package found in db for instance ID %s", instanceID)
	}
	rP := dkgocr.NewResultPackage()
	err = rP.UnmarshalBinary(pack.ReportWithResultPackage)
	if err != nil {
		return nil, nil, fmt.Errorf("could not unmarshal result package: %w", err)
	}

	tdh2PubKey, err := tdh2shim.TDH2PublicKeyFromDKGResult(rP)
	if err != nil {
		return nil, nil, fmt.Errorf("could not get tdh2 public key from DKG result: %w", err)
	}
	publicKey, err = tdh2ToTDH2EasyPK(tdh2PubKey)
	if err != nil {
		return nil, nil, fmt.Errorf("could not convert to tdh2easy public key: %w", err)
	}

	tdh2PrivateKeyShare, err := tdh2shim.TDH2PrivateShareFromDKGResult(rP, r.recipientKey)
	if err != nil {
		return nil, nil, fmt.Errorf("could not get tdh2 private key share from DKG result: %w", err)
	}
	privateKeyShare, err = tdh2ToTDH2EasyKS(tdh2PrivateKeyShare)
	if err != nil {
		return nil, nil, fmt.Errorf("could not convert to tdh2easy private key share: %w", err)
	}

	return publicKey, privateKeyShare, nil
}
```

**File:** core/services/ocr2/plugins/vault/orm.go (L67-83)
```go
func (o *orm) ReadResultPackage(ctx context.Context, iid dkgocrtypes.InstanceID) (*dkgocrtypes.ResultPackageDatabaseValue, error) {
	var configDigest []byte
	var seqNr uint64
	var reportWithResultPackage []byte
	var signatures pq.ByteaArray
	var signerOracleIDs []byte

	query := `SELECT config_digest, seq_nr, report_with_result_package, signatures, signer_oracle_ids FROM dkg_results WHERE instance_id = $1;`
	row := o.ds.QueryRowxContext(ctx, query, iid)
	err := row.Scan(&configDigest, &seqNr, &reportWithResultPackage, &signatures, &signerOracleIDs)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, nil
	}
	if err != nil {
		return nil, errors.Wrap(err, "failed to read dkg result")
	}

```

**File:** core/store/migrate/migrations/0278_create_dkg_results_table.sql (L1-11)
```sql
-- +goose Up
CREATE TABLE dkg_results (
    instance_id TEXT PRIMARY KEY,
    config_digest BYTEA NOT NULL,
    seq_nr BIGINT NOT NULL,
    report_with_result_package BYTEA NOT NULL,
    signatures BYTEA[] NOT NULL,
    signer_oracle_ids BYTEA NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
```

**File:** core/web/vault_controller_test.go (L203-252)
```go
func TestVaultController_ExportDKGResult(t *testing.T) {
	t.Parallel()

	client, keystore, orm := setupVaultControllerTests(t)

	keys, err := keystore.DKGRecipient().GetAll()
	require.NoError(t, err)
	require.Len(t, keys, 1)

	keyrings := []dkgocrtypes.P256Keyring{keys[0]}
	instanceID := dkgocrtypes.InstanceID("test-instance-id")
	rp, err := dummydkg.NewResultPackage(instanceID, dkgocrtypes.ReportingPluginConfig{
		DealerPublicKeys:    []dkgocrtypes.P256ParticipantPublicKey{keys[0].PublicKey()},
		RecipientPublicKeys: []dkgocrtypes.P256ParticipantPublicKey{keys[0].PublicKey()},
		T:                   1,
	}, keyrings)
	require.NoError(t, err)

	rpb, err := rp.MarshalBinary()
	require.NoError(t, err)

	var configDigest types.ConfigDigest
	copy(configDigest[:], common.Hex2Bytes("1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"))
	signatures := []types.AttributedOnchainSignature{
		{
			Signature: common.Hex2Bytes("deadbeef"),
			Signer:    commontypes.OracleID(1),
		},
		{
			Signature: common.Hex2Bytes("cafebabe"),
			Signer:    commontypes.OracleID(2),
		},
	}
	err = orm.WriteResultPackage(t.Context(), instanceID, dkgocrtypes.ResultPackageDatabaseValue{
		ConfigDigest:            configDigest,
		SeqNr:                   1,
		ReportWithResultPackage: rpb,
		Signatures:              signatures,
	})
	require.NoError(t, err)

	bdata, err := json.Marshal(web.ExportDKGResultRequest{
		InstanceID: string(instanceID),
	})
	require.NoError(t, err)

	resp, cleanup := client.Post("/v2/vault/dkg_results/export", bytes.NewReader(bdata))
	t.Cleanup(cleanup)
	cltest.AssertServerResponse(t, resp, http.StatusOK)
}
```
