# [M] Tonic has remotely exploitable denial of service vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4jwc-w2hc-78qv
CVE: CVE-2024-47609
CWE: CWE-755
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-10-01
Source: https://github.com/advisories/GHSA-4jwc-w2hc-78qv
Type: github-advisory

## Affected
- crates.io: `tonic` — affected >=0.12.2 <0.12.3

## Details
### Impact

When using `tonic::transport::Server` there is a remote DoS attack that can cause the server to exit cleanly on accepting a tcp/tls stream. This can be triggered via causing the accept call to error out with errors there were not covered correctly causing the accept loop to exit. 

More information can be found [here](https://github.com/hyperium/tonic/issues/1897)

### Patches

Upgrading to tonic `0.12.3` and above contains the fix. 

### Workarounds

A custom accept loop is a possible workaround.

## References
- https://github.com/hyperium/tonic/security/advisories/GHSA-4jwc-w2hc-78qv
- https://nvd.nist.gov/vuln/detail/CVE-2024-47609
- https://github.com/hyperium/tonic/issues/1897
- https://github.com/hyperium/tonic/commit/a4472a86f3290e60c7c01348b7e6a8164d6e7e48
- https://github.com/hyperium/tonic
- https://rustsec.org/advisories/RUSTSEC-2024-0376.html
