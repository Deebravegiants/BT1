# [H] CVE-2021-25836

## Summary
Severity: High
Advisory: CVE-2021-25836
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-02-08
Source: https://osv.dev/vulnerability/CVE-2021-25836
Type: osv

## Details
Cosmos Network Ethermint <= v0.4.0 is affected by cache lifecycle inconsistency in the EVM module. The bytecode set in a FAILED transaction wrongfully remains in memory(stateObject.code) and is further written to persistent store at the Endblock stage, which may be utilized to build honeypot contracts.

## References
- https://github.com/cosmos/ethermint/issues/667#issuecomment-759284303
