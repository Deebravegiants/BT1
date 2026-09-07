# [M] DragonFly vulnerable to panics due to nil pointer dereference when using variables created alongside an error

## Summary
Severity: Medium
Advisory: GHSA-4mhv-8rh3-4ghw
CVE: CVE-2025-59351
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-4mhv-8rh3-4ghw
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
We found two instances in the DragonFly codebase where the first return value of a function is dereferenced even when the function returns an error (figures 9.1 and 9.2). This can result in a nil dereference, and cause code to panic. The codebase may contain additional instances of the bug.

```golang
request, err := source.NewRequestWithContext(ctx, parentReq.Url,
parentReq.UrlMeta.Header)
if err != nil {
       log.Errorf("generate url [%v] request error: %v", request.URL, err)
       span.RecordError(err)
       return err
}
```

Eve is a malicious actor operating a peer machine. She sends a dfdaemonv1.DownRequest request to her peer Alice. Alice’s machine receives the request, resolves a nil variable in the server.Download method, and panics.

### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-4mhv-8rh3-4ghw
- https://nvd.nist.gov/vuln/detail/CVE-2025-59351
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3970
