# [M] Shallow copy bug in geth

## Summary
Severity: Medium
Advisory: GHSA-69v6-xc2j-r2jf
CVE: CVE-2020-26241
CWE: CWE-682
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-69v6-xc2j-r2jf
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=1.9.7 <1.9.17

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

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-69v6-xc2j-r2jf
- https://nvd.nist.gov/vuln/detail/CVE-2020-26241
- https://github.com/ethereum/go-ethereum/commit/295693759e5ded05fec0b2fb39359965b60da785
- https://blog.ethereum.org/2020/11/12/geth_security_release
- https://github.com/ethereum/go-ethereum
