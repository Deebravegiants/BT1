# [M] Incorrect parsing of EVM reversion exit reason in RPC

## Summary
Severity: Medium
Advisory: GHSA-mjvm-mhgc-q4gp
CVE: CVE-2022-36008
CWE: CWE-190
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-08-18
Source: https://github.com/advisories/GHSA-mjvm-mhgc-q4gp
Type: github-advisory

## Affected
- crates.io: `fc-rpc` — affected >=0

## Details
### Impact

A low severity security issue was discovered affecting parsing of the RPC result of the exit reason in case of EVM reversion. In release build, this would cause the exit reason being incorrectly parsed and returned by RPC. In debug build, this would cause an overflow panic.

No action is needed unless you have a bridge node that needs to distinguish different reversion exit reasons and you used RPC for this.

### Patches

The issue is patched in https://github.com/paritytech/frontier/pull/820

### Workarounds

None.

### References

PR https://github.com/paritytech/frontier/pull/820

### For more information

If you have any questions or comments about this advisory:
* Email [Wei Tang](mailto:wei@that.world)

## References
- https://github.com/paritytech/frontier/security/advisories/GHSA-mjvm-mhgc-q4gp
- https://nvd.nist.gov/vuln/detail/CVE-2022-36008
- https://github.com/paritytech/frontier/pull/820
- https://github.com/paritytech/frontier/commit/fff8cc43b7756ce3979a38fc473f38e6e24ac451
- https://github.com/paritytech/frontier
