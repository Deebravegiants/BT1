# [M] DragonFly vulnerable to arbitrary file read and write on a peer machine

## Summary
Severity: Medium
Advisory: GHSA-79hx-3fp8-hj66
CVE: CVE-2025-59352
CWE: CWE-202, CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-79hx-3fp8-hj66
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
A peer exposes the gRPC API and HTTP API for consumption by other peers. These APIs allow peers to send requests that force the recipient peer to create files in arbitrary file system locations, and to read arbitrary files. This allows peers to steal other peers’ secret data and to gain remote code execution (RCE) capabilities on the peer’s machine.

```golang
file, err := os.OpenFile(t.DataFilePath, os.O_RDWR, defaultFileMode)
if err != nil {
       return 0, err
}
defer file.Close()
if _, err = file.Seek(req.Range.Start, io.SeekStart); err != nil {
       return 0, err
}
n, err := io.Copy(file, io.LimitReader(req.Reader, req.Range.Length))
```

### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-79hx-3fp8-hj66
- https://nvd.nist.gov/vuln/detail/CVE-2025-59352
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3961
