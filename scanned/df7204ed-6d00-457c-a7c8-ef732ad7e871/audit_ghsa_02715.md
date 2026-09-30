# [H] Incorrect handling of H2 GOAWAY + SETTINGS frames

## Summary
Severity: High
Advisory: GHSA-gjcg-vrxg-xmgv
CVE: CVE-2021-39162
CWE: CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-10
Source: https://github.com/advisories/GHSA-gjcg-vrxg-xmgv
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0 <0.15.1

## Details
Envoy, which Pomerium is based on, can abnormally terminate if an H/2 GOAWAY and SETTINGS frame are received in the same IO event.  

### Impact
This can lead to a DoS in the presence of untrusted *upstream* servers.

### Patches
0.15.1 contains an upgraded envoy binary with this vulnerability patched.

### Workarounds
If only trusted upstreams are configured, there is not substantial risk of this condition being triggered.

### References
[envoy GSA](https://github.com/envoyproxy/envoy/security/advisories/GHSA-j374-mjrw-vvp8)
[envoy CVE](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-32780)
[envoy announcement](https://groups.google.com/g/envoy-announce/c/5xBpsEZZDfE/m/wD05NZBbAgAJ)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [pomerium/pomerium](https://github.com/pomerium/pomerium/issues)
* Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-j374-mjrw-vvp8
- https://github.com/pomerium/pomerium/security/advisories/GHSA-gjcg-vrxg-xmgv
- https://nvd.nist.gov/vuln/detail/CVE-2021-39162
- https://github.com/pomerium/pomerium
- https://groups.google.com/g/envoy-announce/c/5xBpsEZZDfE/m/wD05NZBbAgAJ
