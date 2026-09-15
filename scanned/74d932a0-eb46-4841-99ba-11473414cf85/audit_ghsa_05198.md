# [M] Armeria: External Control of File Name or Path in xDS SDS DataSource

## Summary
Severity: Medium
Advisory: GHSA-hgw6-8c77-v4gq
CVE: CVE-2026-11752
CWE: CWE-73
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-hgw6-8c77-v4gq
Type: github-advisory

## Affected
- Maven: `com.linecorp.armeria:armeria-xds` — affected >=0 <1.40.0

## Details
## External Control of File Name or Path in xDS SDS DataSource

### Summary

`DataSourceStream` in the `:xds` module resolves control-plane-supplied `filename` and `environment_variable` fields from SDS Secret resources without any allow-list or base-directory confinement. A semi-trusted or compromised xDS control plane (or an attacker who can MITM SDS responses) can read arbitrary local files and environment variables on the xDS client host.

**Affected component:** `xds/src/main/java/com/linecorp/armeria/xds/DataSourceStream.java`
**Introduced in:** Armeria 1.38.0 (commit `b199560b10`, "Add support for SDS", #6597)
**Affected versions:** 1.38.0, 1.39.0

### Impact

A semi-trusted or compromised xDS control plane (or an attacker who can inject/MITM SDS responses) can:

- **Read arbitrary files** on the xDS client host — TLS private keys, `/etc/passwd`, mounted Kubernetes service-account tokens, cloud credential files, etc.
- **Read arbitrary environment variables** — `AWS_SECRET_ACCESS_KEY`, CI tokens, database credentials, etc.

The read bytes are consumed as TLS key/cert/CA material. Combined with CWE-295 (silent disabling of upstream TLS peer verification), the exfiltrated secret can be presented to an attacker-chosen upstream, enabling data exfiltration. This is a confused-deputy / information-disclosure primitive driven entirely by control-plane-supplied configuration.

**Severity:** High — arbitrary host-level file and environment variable read via control-plane-pushed configuration.

### Patches

1.40.0

The fix should:

1. **Confine `filename` resolution** to an operator-configured allow-list of base directories. After normalization, reject any path that escapes the allow-listed root.
2. **Gate `environment_variable`** behind an explicit operator allow-list of permitted variable names.
3. **Default to denying** both `filename` and `environment_variable` DataSources for control-plane-delivered (SDS) secrets unless explicitly enabled by the operator. This is stricter than upstream Envoy but appropriate when the control plane is not fully trusted.
4. **Document the trust model** clearly so operators understand that enabling file/env DataSources grants the control plane host-level read capability.

### Workarounds

- Ensure the xDS control plane channel is authenticated and encrypted (mTLS) to prevent MITM injection of malicious SDS responses.
- Run the xDS client with minimal filesystem permissions and a restricted environment to limit the blast radius of arbitrary reads.
- If SDS file-based secrets are not needed, consider using inline `DataSource` bytes only (delivered over the SDS stream itself) and auditing control-plane configurations to ensure no `filename` or `environment_variable` DataSources are present.

## References
- https://github.com/line/armeria/security/advisories/GHSA-hgw6-8c77-v4gq
- https://nvd.nist.gov/vuln/detail/CVE-2026-11752
- https://github.com/line/armeria
- https://github.com/line/armeria/security/advisories/xds/src/main/java/com/linecorp/armeria/xds/DataSourceStream.java
