# [H] A malicious transaction object can trigger a Node DoS

## Summary
Severity: High
Contest weight: 0.7870
Dataset id: 3799
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Berachain uses forked versions of various ssz libraries including https://github.com/itsdevbear/ssz, which is forked from https://github.com/karalabe/ssz. This library implements HashStaticBytes():
```solidity
func HashStaticBytes[T commonBytesLengths](h *Hasher, blob *T) {
// The code below should have used `blob[:]`, alas Go's generics compiler
// is missing that (i.e. a bug): https://github.com/golang/go/issues/51740
h.hashBytes(unsafe.Slice(&(*blob)[0], len(*blob)))
}
```
This function takes in any type whose underlying type is that of commonBytesLengths. Which is defined in the
upstream repository as any type whose underlying type is a byte array of the following sizes here:
```solidity
type commonBytesLengths interface {
// fork | nonce | address | verkle-stem | hash | pubkey | committee | signature | bloom
~[4]byte | ~[8]byte | ~[20]byte | ~[31]byte | ~[32]byte | ~[48]byte | ~[64]byte | ~[96]byte | ~[256]byte
}
```
An issue was introduced when a change to this interface was made in the berachain-used fork that added the
variable byte array size ~[]byte:
```solidity
type commonBytesLengths interface {
// fork | address | verkle-stem | hash | pubkey | committee | signature | bloom | blob & tx
~[4]byte | ~[20]byte | ~[31]byte | ~[32]byte | ~[48]byte | ~[64]byte | ~[96]byte | ~[256]byte | ~[131072]byte | ~[]byte
}
```
This addition allows for any function that accepts this interface type to accept an array of any size, including
a 0-length array, introducing a panic: runtime error: index out of range [0] with length 0 when the 0
indexing of the blob object is done. This is exposed in the dependencies of transaction processing in Berachain
due to the way Transactions are deserialized when they are hashed. This allows for an attacker to create a
malicious transaction that can crash the beacon-kit process depending on how its execution client sanitizes these
transactions.
This is triggerable from an untrusted buffer when transactions are hashed in /mod/engine-primitives/pkg/engine-primitives/transactions.go and /mod/engine-primitives/pkg/engine-primitives/transactions_bartio.go and was discovered when fuzzing berachain's transaction processing flows.

## Recommendation
Do not modify the commonBytesLengths interface definition to include variable length byte
arrays. If a variable length array is needed then define another byte length type.
