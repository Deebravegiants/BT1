# [M] OpenZeppelin Contracts contains Improper Verification of Cryptographic Signature

## Summary
Severity: Medium
Chain: openzeppelin-cairo-contracts
Component: openzeppelin-cairo-contracts
CVE: CVE-2023-23940
CWE: Insufficient Verification of Data Authenticity, Improper Verification of Cryptographic Signature
Published: 2023-02-02
Source: https://github.com/advisories/GHSA-626q-v9j4-mcp4
Type: github-advisory

## Details
### Cause
`is_valid_eth_signature` is missing a call to `finalize_keccak` after calling `verify_eth_signature`. 

### Impact
As a result, any contract using `is_valid_eth_signature` from the account library (such as the `EthAccount` preset) is vulnerable to a malicious sequencer. Specifically, the malicious sequencer would be able to bypass signature validation to impersonate an instance of these accounts.

### Risk
In order to exploit this vulnerability, it is required to control a sequencer or prover since they're the ones executing the hints, being able to inject incorrect keccak results.

Today StarkWare is the only party running both a prover or a sequencer, greatly reducing the risk of exploit.

### Patches
The issue has been patched in 0.6.1.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Contracts for Cairo repository](https://github.com/OpenZeppelin/cairo-contracts/issues/new/choose)
* Email us at [security@openzeppelin.com](mailto:security@openzeppelin.com)
