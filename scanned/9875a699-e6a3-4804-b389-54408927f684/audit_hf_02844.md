# [M] Vulnerable Packages

## Summary
Severity: Medium
Contest weight: 0.1672
Dataset id: 15845
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Currently, the protocol uses two vulnerable packages.
Timing variability in curve25519-dalek's Scalar29::sub/Scalar52::sub
Timing variability of any kind is problematic when working with potentially secret values such as elliptic curve scalars, and such issues can potentially leak private keys and other secrets.
Reference - https://rustsec.org/advisories/RUSTSEC-2024-0344
Double Public Key Signing Function Oracle Attack on `ed25519-dalek`
Versions of ed25519-dalek prior to v2.0 model private and public keys as separate types which can be assembled into a Keypair, and also provide APIs for serializing and deserializing 64-byte private/public keypairs.
Such APIs and serializations are inherently unsafe as the public key is one of the inputs used in the deterministic computation of the S part of the signature, but not in the R value. An adversary could somehow use the signing function as an oracle that allows arbitrary public keys as input can obtain two signatures for the same message sharing the same R and only differ on the S part.
Unfortunately, when this happens, one can easily extract the private key.
Reference - https://rustsec.org/advisories/RUSTSEC-2022-0093

## Recommendation
Have a look in the reference in which version the vulnerabilities are fixed and update at least to that version.
