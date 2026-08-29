# [H] Shallow copy in the 0x4 precompile could lead to EVM memory corruption

## Summary
Severity: High
Chain: Ethereum
Component: ethereum/go-ethereum
CVE: CVE-2020-26241
Published: 2020-11-24
Source: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-69v6-xc2j-r2jf
Type: github-advisory

## Details
### Impact
This is a Consensus vulnerability, which can be used to cause a chain-split where vulnerable nodes reject the canonical chain. 

Geth’s pre-compiled `dataCopy` (at `0x00...04`) contract did a shallow copy on invocation. An attacker could deploy a contract that 

- writes `X` to an EVM memory region `R`,
- calls `0x00..04` with `R` as an argument,
- overwrites `R` to `Y`,
- and finally invokes the `RETURNDATACOPY` opcode.

When this contract is invoked, a consensus-compliant node would push `X` on the EVM stack, whereas Geth would push `Y`.


### Patches

No standalone patches have been made. 

### Workarounds

Upgrade to `1.9.17` or higher.

### References

https://blog.ethereum.org/2020/11/12/geth_security_release/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-ethereum](https://github.com/ethereum/go-ethereum)
* Email us at [security@ethereum.org](mailto:security@ethereum.org)
