# [M] ydb-go-sdk token in custom credentials object can leak through logs

## Summary
Severity: Medium
Advisory: GHSA-q24m-6h38-5xj8
CVE: CVE-2023-45825
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-q24m-6h38-5xj8
Type: github-advisory

## Affected
- Go: `github.com/ydb-platform/ydb-go-sdk/v3` — affected >=3.48.6 <3.53.3

## Details
### Impact
Since [ydb-go-sdk/v3.48.6](https://github.com/ydb-platform/ydb-go-sdk/blob/v3.48.6/internal/balancer/balancer.go#L71) if you use a custom credentials object (implementation of interface [Credentials](https://github.com/ydb-platform/ydb-go-sdk/blob/master/credentials/credentials.go#L10)) it may leak into logs. This happens because this object could be serialized into an error message using `fmt.Errorf("something went wrong (credentials: %q)", credentials)` during connection to the YDB server. Printf func use placeholder `%q` for string representation of argument with quotes. If an argument implements interface `fmt.Stringer`, it will used through `String()` func. In other cases used fallback - serialization with reflection.

If such logging occurred, a  malicious user with access to logs could read sensitive information (i.e. credentials) information and use it to get access to the database.

Who is impacted: applications with custom credentials object with an explicit token field.

A leak could have occurred if all of these conditions were met simultaneously:
1) The credentials object does not implement the `fmt.Stringer` interface (does not have a `String()` method) - potentially these are custom credentials. Official credentials have a `String()` method.
2) There was an error connecting to YDB during driver creation via `ydb.Open(...)`.
3) Some logging system was configured (`ydb-go-sdk` does not log such errors by default).
4) The connection error was logged into a system that a malicious user had access to.

### Patches
`ydb-go-sdk` contains this problem in versions from v3.48.6 to v3.53.2. The fix for this problem has been released in version v3.53.3 ([PR](https://github.com/ydb-platform/ydb-go-sdk/pull/859)).

### Workarounds
Implement the `fmt.Stringer` interface in your custom credentials type with explicit stringify of object state.

## References
- https://github.com/ydb-platform/ydb-go-sdk/security/advisories/GHSA-q24m-6h38-5xj8
- https://nvd.nist.gov/vuln/detail/CVE-2023-45825
- https://github.com/ydb-platform/ydb-go-sdk/pull/859
- https://github.com/ydb-platform/ydb-go-sdk/commit/a0d92057c4e1bbdc5e85ae8d649edb0232b8fd4c
- https://github.com/ydb-platform/ydb-go-sdk
- https://github.com/ydb-platform/ydb-go-sdk/blob/master/credentials/credentials.go#L10
- https://github.com/ydb-platform/ydb-go-sdk/blob/v3.48.6/internal/balancer/balancer.go#L71
