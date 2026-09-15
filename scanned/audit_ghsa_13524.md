# [M] Vapor's incorrect request error handling triggers server crash

## Summary
Severity: Medium
Advisory: GHSA-3mwq-h3g6-ffhm
CVE: CVE-2023-44386
CWE: CWE-231
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-10-05
Source: https://github.com/advisories/GHSA-3mwq-h3g6-ffhm
Type: github-advisory

## Affected
- SwiftURL: `github.com/vapor/vapor` — affected >=4.83.2 <4.84.2

## Details
Vapor incorrectly handles errors encountered during parsing of HTTP 1.x requests, triggering a precondition failure in swift-nio due to API misuse and causing immediate termination of the server process.

### Impact
This is a denial of service vulnerability, impacting all users of affected versions of Vapor. Because the crash is an explicit assertion failure, there is no corruption of process state and no risk of data leakage or unauthorized code execution. Total impact is limited to an immediately recoverable service interruption.

### Patches
The issue is fixed as of Vapor release 4.84.2.

### Workarounds
None known at this time.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Vapor repo](https://github.com/vapor/vapor)
* Ask in [Vapor Discord](http://vapor.team)

### Acknowledgements

Full credit for reporting this issue goes to @t0rchwo0d, with additional thanks for responsibly disclosing.

## References
- https://github.com/vapor/vapor/security/advisories/GHSA-3mwq-h3g6-ffhm
- https://nvd.nist.gov/vuln/detail/CVE-2023-44386
- https://github.com/vapor/vapor/commit/090464a654b03148b139a81f8f5ac63b0856f6f3
- https://github.com/vapor/vapor
- https://github.com/vapor/vapor/releases/tag/4.84.2
