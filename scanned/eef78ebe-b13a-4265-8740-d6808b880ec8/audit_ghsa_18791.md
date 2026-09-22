# [H] Constellation has insecure LUKS2 persistent storage partitions which may be opened and used

## Summary
Severity: High
Advisory: GHSA-hq76-6gh2-5g4q
CVE: CVE-2025-58356
CWE: CWE-347, CWE-552
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-hq76-6gh2-5g4q
Type: github-advisory

## Affected
- Go: `github.com/edgelesssys/constellation/v2` — affected >=0 <2.24.0

## Details
### Summary
A malicious host may provide a crafted LUKS2 volume to a confidential computing guest that is using the [OpenCryptDevice](https://github.com/edgelesssys/constellation/blob/6eff250f16f8ae48221d412550e4a64a4bf0d77b/csi/cryptmapper/cryptmapper.go#L89) feature. The guest will open the volume and write secret data using a volume key known to the attacker. The attacker can also pre-load data on the device, which could potentially compromise guest execution.


LUKS2 volume metadata is not authenticated and supports null key-encryption algorithms, allowing an attacker to create a volume such that the volume:
- Opens (cryptsetup open) without error using any passphrase or token
- Records all writes in plaintext (or ciphertext with an attacker-known key)
- Contains arbitrary data chosen by the attacker


### Details
The Constellation CVM image uses LUKS2-encrypted volumes for persistent storage. When opening an encrypted storage device, the CVM uses the `libcryptsetup`  function [crypt_activate_by_passhrase](https://github.com/martinjungblut/go-cryptsetup/blob/fd0874fd07a6e477f0a4d18f2e80234983afe74f/device.go#L261). If the VM is successful in opening the partition with the disk encryption key, it treats the volume as confidential. However, due to the unsafe handling of null keyslot algorithms in the cryptsetup 2.8.1,  it is possible that the opened volume is not encrypted at all.

Cryptsetup prior to version 2.8.1 does not report an error when processing LUKS2-formatted disks that use the `cipher_null-ecb` algorithm in the keyslot `encryption` field.

### Impact

A LUKS2 disk encrypted with a master key, which is in turn encrypted with user passwords stored in some number of keyslots. By creating a malicious disk which sets the keyslot encryption algorithm to `”crypto_null-ecb”`, an attacker can construct a disk such that keyslot decryption does not depend in any way on the enclave-held secret data. When a confidential guest opens such a device using `cryptsetup open`, the mapped disk is created without error, and any further writes to the disk are encrypted using an attacker-controlled key.

### Patches

To protect against this and similar attacks, Constellation now performs detached reading of LUKS headers. The header is copied into the encrypted memory of the CVM and then verified. The verified header is then used to open the encrypted LUKS device in detached header mode. This was implemented in https://github.com/edgelesssys/constellation/pull/3927 and release as part of [Constellation v2.24.0](https://github.com/edgelesssys/constellation/releases/tag/v2.24.0).

## References
- https://github.com/edgelesssys/constellation/security/advisories/GHSA-hq76-6gh2-5g4q
- https://nvd.nist.gov/vuln/detail/CVE-2025-58356
- https://github.com/edgelesssys/constellation/pull/3927
- https://github.com/edgelesssys/constellation/commit/bb8d2c8a5c0a0a6510d2cc43055be21f4a3ab83c
- https://blog.trailofbits.com/2025/10/30/vulnerabilities-in-luks2-disk-encryption-for-confidential-vms
- https://github.com/edgelesssys/constellation
- https://github.com/edgelesssys/constellation/releases/tag/v2.24.0
