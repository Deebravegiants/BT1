# [H] Incorrect Authorization with specially crafted requests

## Summary
Severity: High
Advisory: GHSA-cfc2-wjcm-c8fm
CVE: CVE-2021-39206
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-10
Source: https://github.com/advisories/GHSA-cfc2-wjcm-c8fm
Type: github-advisory

## Affected
- Go: `github.com/pomerium/pomerium` — affected >=0.11.0 <0.14.8
- Go: `github.com/pomerium/pomerium` — affected >=0.15.0 <0.15.1

## Details
Envoy, which Pomerium is based on, contains two authorization related vulnerabilities:

- [CVE-2021-32777](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-32779): incorrectly transform a URL containing a `#fragment` element, causing a mismatch in path-prefix based authorization decisions.
- [CVE-2021-32779](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-32777): incorrectly handle duplicate headers, dropping all but the last.  This may lead to incorrect routing or authorization policy decisions.

### Impact
With specially crafted requests, incorrect authorization or routing decisions may be made by Pomerium.

### Patches

Pomerium v0.14.8 and v0.15.1 contain an upgraded envoy binary with these vulnerabilities patched.

### Workarounds

- This issue can only be triggered when using path prefix based policy.  Removing any such policies should provide mitigation.


### References
[envoy GSA CVE-2021-32777](https://github.com/envoyproxy/envoy/security/advisories/GHSA-r222-74fw-jqr9)
[envoy GSA CVE-2021-32779](https://github.com/envoyproxy/envoy/security/advisories/GHSA-6g4j-5vrw-2m8h)
[envoy announcement](https://groups.google.com/g/envoy-announce/c/5xBpsEZZDfE/m/wD05NZBbAgAJ)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [pomerium/pomerium](https://github.com/pomerium/pomerium/issues)
* Email us at [security@pomerium.com](mailto:security@pomerium.com)

## References
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-6g4j-5vrw-2m8h
- https://github.com/envoyproxy/envoy/security/advisories/GHSA-r222-74fw-jqr9
- https://github.com/pomerium/pomerium/security/advisories/GHSA-cfc2-wjcm-c8fm
- https://nvd.nist.gov/vuln/detail/CVE-2021-39206
- https://github.com/pomerium/pomerium
- https://groups.google.com/g/envoy-announce/c/5xBpsEZZDfE/m/wD05NZBbAgAJ
