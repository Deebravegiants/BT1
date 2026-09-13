# [H] Excessive CPU usage

## Summary
Severity: High
Advisory: GHSA-5wjf-62hw-q78r
CVE: CVE-2021-39204
CWE: CWE-834
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-10
Source: https://github.com/advisories/GHSA-5wjf-62hw-q78r
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0 <0.14.8
- Go: `github.com/pomerium/pomerium` — affected >=0.15.0 <0.15.1

## Details
Envoy, which Pomerium is based on, incorrectly handles resetting of HTTP/2 streams with excessive complexity.  This can lead to high CPU utilization when a large number of streams are reset.  

### Impact

This can result in a DoS condition.

### Patches
Pomerium versions 0.14.8 and 0.15.1 contain an upgraded envoy binary with this vulnerability patched.

### Workarounds
N/A

### References
[envoy GSA](https://github.com/envoyproxy/envoy/security/advisories/GHSA-3xh3-33v5-chcc)
[envoy CVE](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-32778)
[envoy announcement](https://groups.google.com/g/envoy-announce/c/5xBpsEZZDfE/m/wD05NZBbAgAJ)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [pomerium/pomerium](https://github.com/pomerium/pomerium/issues)
* Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-3xh3-33v5-chcc
- https://github.com/pomerium/pomerium/security/advisories/GHSA-5wjf-62hw-q78r
- https://nvd.nist.gov/vuln/detail/CVE-2021-39204
- https://github.com/pomerium/pomerium
- https://groups.google.com/g/envoy-announce/c/5xBpsEZZDfE/m/wD05NZBbAgAJ
