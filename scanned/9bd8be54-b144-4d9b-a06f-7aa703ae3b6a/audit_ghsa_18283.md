# [M] Dragonfly's manager makes requests to external endpoints with disabled TLS authentication

## Summary
Severity: Medium
Advisory: GHSA-98x5-jw98-6c97
CVE: CVE-2025-59347
CWE: CWE-287, CWE-295
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-98x5-jw98-6c97
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact

The Manager disables TLS certificate verification in two HTTP clients (figures 3.1 and 3.2). The clients are not configurable, so users have no way to re-enable the verification.

```golang
func getAuthToken(ctx context.Context, header http.Header) (string, error) { [skipped]
       client := &http.Client{
             Timeout: defaultHTTPRequesttimeout,
             Transport: &http.Transport{
                    TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
             },
}
[skipped]
}
```

A Manager processes dozens of preheat jobs. An adversary performs a network-level Man-in-the-Middle attack, providing invalid data to the Manager. The Manager preheats with the wrong data, which later causes a denial of service and file integrity problems.

### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-98x5-jw98-6c97
- https://nvd.nist.gov/vuln/detail/CVE-2025-59347
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3966
