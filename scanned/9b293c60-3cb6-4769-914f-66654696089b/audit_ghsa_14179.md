# [H] SpiceDB binding metrics port to untrusted networks and can leak command-line flags

## Summary
Severity: High
Advisory: GHSA-cjr9-mr35-7xh6
CVE: CVE-2023-29193
CWE: CWE-209
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-04-13
Source: https://github.com/advisories/GHSA-cjr9-mr35-7xh6
Type: github-advisory

## Affected
- Go: `github.com/authzed/spicedb` — affected >=0 <1.19.1

## Details
### Background

The `spicedb serve` command contains a flag named `--grpc-preshared-key` which is used to protect the gRPC API from being accessed by unauthorized requests. The values of this flag are to be considered sensitive, secret data.

The `/debug/pprof/cmdline` endpoint served by the metrics service (defaulting running on port `9090`) reveals the command-line flags provided for debugging purposes. If a password is set via the `--grpc-preshared-key` then the key is revealed by this endpoint along with any other flags provided to the SpiceDB binary.

### Impact

All deployments abiding by the recommended best practices for production usage are **NOT affected**:
- Authzed's SpiceDB Serverless
- Authzed's SpiceDB Dedicated
- SpiceDB Operator

Users configuring SpiceDB via environment variables are **NOT affected**.

Users **MAY be affected** if they expose their metrics port to an untrusted network and are configuring `--grpc-preshared-key` via command-line flag.

### Workarounds

To workaround this issue you can do one of the following:

- Configure the preshared key via an environment variable (e.g. `SPICEDB_GRPC_PRESHARED_KEY=yoursecret spicedb serve`)
- Reconfigure the `--metrics-addr` flag to bind to a trusted network (e.g. `--metrics-addr=localhost:9090`)
- Disable the metrics service via the flag (e.g. `--metrics-enabled=false`)
- Adopt one of the recommended deployment models: [Authzed's managed services](https://authzed.com/pricing) or the [SpiceDB Operator](https://github.com/authzed/spicedb-operator)

### References

- [GitHub Security Advisory issued for SpiceDB](https://github.com/authzed/spicedb/security/advisories/GHSA-cjr9-mr35-7xh6)
- [Go issue #22085](https://github.com/golang/go/issues/22085) for documenting the risks of exposing pprof to the internet
- [Go issue #42834](https://github.com/golang/go/issues/42834) discusses preventing pprof registration to the default serve mux
- [semgrep rule go.lang.security.audit.net.pprof.pprof-debug-exposure](https://semgrep.dev/r?q=go.lang.security.audit.net.pprof) checks for a variation of this issue

## References
- https://github.com/authzed/spicedb/security/advisories/GHSA-cjr9-mr35-7xh6
- https://nvd.nist.gov/vuln/detail/CVE-2023-29193
- https://github.com/authzed/spicedb/commit/9bbd7d76b6eaba33fe0236014f9b175d21232999
- https://github.com/authzed/spicedb
- https://github.com/authzed/spicedb/releases/tag/v1.19.1
