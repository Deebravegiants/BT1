# [M] 3.1.1.1 Anyone with access to the machine hardware can tamper with keystore or configuration files

## Summary
Severity: Medium
Contest weight: 0.1793
Dataset id: 5153
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Anyone with access to the machine hardware can tamper with the L1 keystore or configuration files related to Batch Poster.
From the gramine docs, allowed-files "are allowed to be created or opened in the enclave unconditionally. In other words, allowed files, directories and devices can be opened for reading/writing and can be created if they do not exist already. Allowed files are not cryptographically hashed and are thus not protected." This has an associated warning that: "It is insecure to allow files containing code or critical information; developers must not allow files blindly! Instead, use trusted or encrypted files."
However, 
nitro-espresso.manifest 
has 
sgx.allowed_files = ["file:/home/user/.arbitrum", "file:/home/user/kzg10-aztec20-srs-1048584.bin", "file:/config", "file:/l1keystore"]. 
The l1keystore will include the signing keys among others and the config may include critical configuration parameters that affect the liveness and security of the system.
Impact: High, because anyone with access to the machine hardware can tamper with the keystore or configuration to affect liveness and security guarantees of the Batch Poster.
Likelihood: Low, because access to machine hardware is presumably guarded with the highest level of OpSec best practices.

## Recommendation
Consider using trusted or encrypted files instead of allowed files for anything that has critical information as noted in the Gramine documentation.
