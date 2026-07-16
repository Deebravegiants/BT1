[File: 'File Name: core/primitives/src/spice/chunk_endorsement.rs -> Scope: Critical. Unprivileged-user-triggered Signature, account key, validator signer, approval, endorsement, VRF, light client, epoch sync proof, or hash-domain bug verifies an invalid proof/signature or rejects a valid one in consensus code.'] [Function: SpiceChunkEndorsement::new / SpiceChunkEndorsementV1::into_verified

### Citations

**File:** core/primitives/src/spice/chunk_endorsement.rs (L133-167)
```rust
pub struct SpiceEndorsementCoreStatement {
    account_id: AccountId,
    signature: Signature,
    signed_data: SpiceEndorsementSignedData,
}

impl SpiceEndorsementCoreStatement {
    pub fn chunk_id(&self) -> &SpiceChunkId {
        &self.signed_data.chunk_id
    }

    pub fn account_id(&self) -> &AccountId {
        &self.account_id
    }

    pub fn verified_signed_data(
        &self,
        public_key: &PublicKey,
    ) -> Option<(&SpiceEndorsementSignedData, &Signature)> {
        let data = &self.signed_data.serialize_data_for_signing();
        if !self.signature.verify(data, public_key) {
            return None;
        }
        Some((&self.signed_data, &self.signature))
    }

    /// Converts to SpiceStoredVerifiedEndorsement without signature verification.
    /// Caller should make sure that relevant core statement is validated.
    pub fn unchecked_to_stored(&self) -> SpiceStoredVerifiedEndorsement {
        SpiceStoredVerifiedEndorsement {
            execution_result_hash: self.signed_data.execution_result_hash.clone(),
            signature: self.signature.clone(),
        }
    }
}
```

**File:** core/primitives/src/spice/chunk_endorsement.rs (L175-181)
```rust
impl SpiceEndorsementSignedData {
    fn serialize_data_for_signing(&self) -> Vec<u8> {
        static SIGNATURE_DIFFERENTIATOR: StaticSignatureDifferentiator =
