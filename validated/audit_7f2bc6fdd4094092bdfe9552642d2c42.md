### Title
BLS12-381 pairing check vacuously succeeds on empty input, enabling signature-check bypass in contracts - (File: runtime/near-vm-runner/src/logic/bls12381.rs)

### Summary
The `bls12381_pairing_check` host function, exposed to every WASM smart contract, computes whether `∏ e(g1_i, g2_i) == 1`. When called with a zero-length input buffer, the implementation never enters its verification loop and returns success (`0`, meaning "pairing product equals identity") without having checked a single point. This mirrors the reported bug class in CL-2021-25, where `aggregateVerify` failed to reject zero-length public-key/message arrays and thus returned "verified" vacuously.

### Finding Description
`pairing_check` in `runtime/near-vm-runner/src/logic/bls12381.rs` only validates that `data.len()` is a multiple of the item size via `check_input_size` (an empty slice trivially satisfies this): [1](#0-0) 

When `elements_count` is `0`, both `blst_g1_list` and `blst_g2_list` are empty, the per-element validation/deserialization loop does not execute, and `pairing_fp12` is left at `blst::blst_fp12::default()` (the multiplicative identity) before `final_exp()` and the `blst_fp12_is_one` check: [2](#0-1) 

Because the identity element trivially satisfies "product equals one", `pairing_check(&[])` returns `Ok(0)` — the same success code used for a legitimately verified non-empty pairing equation. There is no explicit rejection of `elements_count == 0` anywhere in the function or in its caller.

This function is exposed as the WASM host function `bls12381_pairing_check`, callable by any deployed contract from a normal `FunctionCall` action: [3](#0-2) 

### Impact Explanation
Contracts that use `bls12381_pairing_check` as a building block for BLS signature/aggregate-signature verification (e.g., validating a multisig threshold signature, a cross-chain bridge attestation, or a staking-pool authorization scheme) can be tricked into accepting a completely empty proof as "verified" if the calling contract does not itself separately enforce a minimum, non-zero element count. An attacker who can influence the length of the buffer passed to this host function (e.g., by supplying zero signatures/public keys in a contract call) can make the pairing check pass without possessing any valid signature, potentially unlocking unauthorized state changes or fund transfers gated by that contract's signature check. This is a "free/bypassed verification" class bug consistent with the CL-2021-25 analog, not a base-protocol consensus signature bypass (native transaction/receipt signatures use `Signature::verify`/`ed25519_verify`, which are unaffected).

### Likelihood Explanation
High likelihood of exploitability for any contract that relies on `bls12381_pairing_check` without independently validating that the number of pairing terms is non-zero, since the host function is directly and unrestrictedly callable by any account via a standard `FunctionCall` action; no special privilege is required.

### Recommendation
Add an explicit rejection when `elements_count == 0` (or more generally, require a caller-configurable minimum number of pairing terms) in `pairing_check`, returning `HostError::BLS12381InvalidInput` for empty input rather than a spurious "success" (`Ok(0)`), matching the fix pattern applied to `blst-ts`'s `aggregateVerify`.

### Proof of Concept
A contract that calls `bls12381_pairing_check` with `value_len = 0, value_ptr = 0` (i.e., an empty byte buffer) receives return value `0`, which per the function's documented contract means "the pairing result equals the multiplicative identity" — i.e., verification succeeded — even though no G1/G2 points were supplied or checked: [4](#0-3)

### Citations

**File:** runtime/near-vm-runner/src/logic/bls12381.rs (L329-384)
```rust
pub(crate) fn pairing_check(data: &[u8]) -> Result<u64> {
    const ITEM_SIZE: usize = BLS_P1_SIZE + BLS_P2_SIZE;
    check_input_size(data, ITEM_SIZE, "bls12381_pairing_check")?;
    let elements_count = data.len() / ITEM_SIZE;

    let mut blst_g1_list: Vec<blst::blst_p1_affine> =
        vec![blst::blst_p1_affine::default(); elements_count];
    let mut blst_g2_list: Vec<blst::blst_p2_affine> =
        vec![blst::blst_p2_affine::default(); elements_count];

    for (i, item_data) in data.chunks_exact(ITEM_SIZE).enumerate() {
        let (point1_data, point2_data) = item_data.split_at(BLS_P1_SIZE);
        debug_assert_eq!(point2_data.len(), BLS_P2_SIZE);

        if point1_data[0] & 0x80 != 0 {
            return Ok(1);
        }

        let error_code =
            unsafe { blst::blst_p1_deserialize(&mut blst_g1_list[i], point1_data.as_ptr()) };

        if error_code != blst::BLST_ERROR::BLST_SUCCESS {
            return Ok(1);
        }

        let g1_check = unsafe { blst::blst_p1_affine_in_g1(&blst_g1_list[i]) };
        if g1_check == false {
            return Ok(1);
        }

        if point2_data[0] & 0x80 != 0 {
            return Ok(1);
        }

        let error_code =
            unsafe { blst::blst_p2_deserialize(&mut blst_g2_list[i], point2_data.as_ptr()) };
        if error_code != blst::BLST_ERROR::BLST_SUCCESS {
            return Ok(1);
        }

        let g2_check = unsafe { blst::blst_p2_affine_in_g2(&blst_g2_list[i]) };
        if g2_check == false {
            return Ok(1);
        }
    }

    let mut pairing_fp12 = blst::blst_fp12::default();
    for i in 0..elements_count {
        pairing_fp12 *= blst::blst_fp12::miller_loop(&blst_g2_list[i], &blst_g1_list[i]);
    }
    pairing_fp12 = pairing_fp12.final_exp();

    let pairing_res = unsafe { blst::blst_fp12_is_one(&pairing_fp12) };

    if pairing_res { Ok(0) } else { Ok(2) }
}
```

**File:** runtime/near-vm-runner/src/logic/logic.rs (L1473-1486)
```rust
    pub fn bls12381_pairing_check(&mut self, value_len: u64, value_ptr: u64) -> Result<u64> {
        self.result_state.gas_counter.pay_base(bls12381_pairing_base)?;

        const BLS_P1_SIZE: usize = 96;
        const BLS_P2_SIZE: usize = 192;
        const ITEM_SIZE: usize = BLS_P1_SIZE + BLS_P2_SIZE;

        let data = get_memory_or_register!(self, value_ptr, value_len)?;
        let elements_count = data.len() / ITEM_SIZE;

        self.result_state.gas_counter.pay_per(bls12381_pairing_element, elements_count as u64)?;

        super::bls12381::pairing_check(&data)
    }
```
