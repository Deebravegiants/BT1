# [M] Denial of service in geth

## Summary
Severity: Medium
Advisory: GHSA-jm5c-rv3w-w83m
CVE: CVE-2020-26242
CWE: CWE-125, CWE-191, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-29
Source: https://github.com/advisories/GHSA-jm5c-rv3w-w83m
Type: github-advisory

## Affected
- Go: `github.com/ethereum/go-ethereum` — affected >=1.9.16 <1.9.18
- Go: `github.com/holiman/uint256` — affected >=0.1.0 <1.1.1

## Details
### Impact
Denial-of-service (crash) during block processing

### Details

Affected versions suffer from a vulnerability which can be exploited through the `MULMOD` operation, by specifying a modulo of `0`: `mulmod(a,b,0)`, causing a `panic` in the underlying library. 
The crash was in the `uint256` library, where a buffer [underflowed](https://github.com/holiman/uint256/blob/4ce82e695c10ddad57215bdbeafb68b8c5df2c30/uint256.go#L442).

	if `d == 0`, `dLen` remains `0`

and https://github.com/holiman/uint256/blob/4ce82e695c10ddad57215bdbeafb68b8c5df2c30/uint256.go#L451 will try to access index `[-1]`.

The `uint256` library was first merged in this [commit](https://github.com/ethereum/go-ethereum/commit/cf6674539c589f80031f3371a71c6a80addbe454), on 2020-06-08. 
Exploiting this vulnerabilty would cause all vulnerable nodes to drop off the network. 

The issue was brought to our attention through a [bug report](https://github.com/ethereum/go-ethereum/issues/21367), showing a `panic` occurring on sync from genesis on the Ropsten network.
 
It was estimated that the least obvious way to fix this would be to merge the fix into `uint256`, make a new release of that library and then update the geth-dependency.

- https://github.com/holiman/uint256/releases/tag/v1.1.1 was made the same day, 
- PR to address the issue: https://github.com/holiman/uint256/pull/80 
- PR to update geth deps: https://github.com/ethereum/go-ethereum/pull/21368 



### Patches

Upgrade to v1.9.18 or higher

### Workarounds

Not at this time

### References

https://blog.ethereum.org/2020/11/12/geth_security_release/
### For more information
If you have any questions or comments about this advisory:
* Open an issue in [go-ethereum](https://github.com/ethereum/go-ethereum)
* Email us at [security@ethereum.org](mailto:security@ethereum.org)

## References
- https://github.com/ethereum/go-ethereum/security/advisories/GHSA-jm5c-rv3w-w83m
- https://nvd.nist.gov/vuln/detail/CVE-2020-26242
- https://github.com/holiman/uint256/pull/80
- https://github.com/ethereum/go-ethereum/commit/7163a6664ee664df81b9028ab3ba13b9d65a7196
- https://github.com/holiman/uint256/commit/6785da6e3eea403260a5760029e722aa4ff1716d
- https://blog.ethereum.org/2020/11/12/geth_security_release
- https://github.com/ethereum/go-ethereum
- https://pkg.go.dev/vuln/GO-2021-0103
