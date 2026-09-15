# [H] Vulnerability in Plonky3, Insufficient checks in the Rust verifier and embedded allocators

## Summary
Severity: High
Chain: ZK
Component: succinctlabs/sp1
Published: 2025-06-03
Source: https://github.com/succinctlabs/sp1/security/advisories/GHSA-6248-228x-mmvh
Type: github-advisory

## Details
SP1 was affected by the first Plonky3 vulnerability from the [recent security disclosure](https://github.com/Plonky3/Plonky3/security/advisories/GHSA-f69f-5fx9-w9r9). This affected both the Rust verifier and the on-chain verifiers, and allowed malicious prover to prove incorrect statements. 

The following vulnerabilities were found during an audit Succinct commissioned to Zellic. 

In SP1’s Rust verifier, the `verify_compressed`, `verify_shrink`, `verify_deferred_proof` functions determined whether the verification key was valid by checking if its hash was in the precomputed `recursion_vk_map`. However, this was not sufficient to ensure that the `vk_root`, the merkle root of all valid verifying key hashes, is correctly set in the proof. In the on-chain verifier, the `vk_root` at the root proof is checked to be correct, and the recursion circuits assert that this `vk_root` correctly propagates down in the recursion tree, which show that the `vk_root` is correct. In the Rust verifier, there are no such enforcements at the root proof in the `compress`, `shrink`, `deferred` stage, which allows a malicious prover to use an invalid `vk_root`. 

To fix this, we added a check to the Rust verifier that the `vk_root` in the public values is equal to the precomputed `vk_root`. The recursive verifier and the on-chain verifier, as well as the Rust verifier for `wrap` were not affected by this vulnerability as the `vk_root` is correctly checked. 

In SP1’s embedded allocator, when an input is provided by `read_vec_raw`, the allocator checks that it doesn’t overflow the input region by checking that `ptr + capacity` is not larger than `MAX_MEMORY`. However, in this check, the addition did not check overflow, allowing a large `capacity` to make the sum wrap around to a smaller address. This can lead to an arbitrary write for certain type of programs, for example, if a program does two `read_vec` calls then writes into the second buffer. The bump allocator, which is the default allocator used, is not affected. 

Also in SP1’s embedded allocator, the heap starts from `_end` to `EMBEDDED_RESERVED_INPUT_START`, with the heap size being the difference between the two values. However, there was no check to ensure that `_end` is less than or equal to `EMBEDDED_RESERVED_INPUT_START`. If this is not the case, the heap size will overflow and the heap could overlap with the hint area, potentially leading to more security issues. The bump allocator, which is the default allocator used by SP1, is also not affected by this issue. 

Zellic has also suggested to add more compile time checks to the ELF. We have added the check that the area reserved for the stack doesn’t overlap with program data or program space with no data, and updated the Rust compiler flags accordingly. This is not expected to affect users using correctly generated ELFs from secure programs.
