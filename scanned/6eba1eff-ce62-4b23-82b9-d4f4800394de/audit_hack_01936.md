# [M] 6.6 Zero Address EOA Signer Considered Valid

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

isValidSignature() returns true for signer equal to zero address, signatureType EOA and invalid
signature.

The check is performed at line 70 of Signature.sol, SilentECDSA.recover returns 0 on error.
Setting the signer to zero address will incorrectly validate the signature.

Code correct

Signature verification now uses Openzeppelin's ECDSA.recover instead of SilentECDSA. Invalid
signatures now revert instead of returning the 0-address.
