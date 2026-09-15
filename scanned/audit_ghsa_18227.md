# [M] DragonFly's tiny file download uses hard coded HTTP protocol

## Summary
Severity: Medium
Advisory: GHSA-mcvp-rpgg-9273
CVE: CVE-2025-59410
CWE: CWE-311
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-mcvp-rpgg-9273
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
The code in the scheduler for downloading a tiny file is hard coded to use the HTTP protocol, rather than HTTPS. This means that an attacker could perform a Man-in-the-Middle attack, changing the network request so that a different piece of data gets downloaded. Due to the use of weak integrity checks (TOB-DF2-15), this modification of the data may go unnoticed.

```golang
// DownloadTinyFile downloads tiny file from peer without range.
func (p *Peer) DownloadTinyFile() ([]byte, error) {
       ctx, cancel := context.WithTimeout(context.Background(),
downloadTinyFileContextTimeout)
       defer cancel()
       // Download url:
http://${host}:${port}/download/${taskIndex}/${taskID}?peerId=${peerID}
       targetURL := url.URL{
Scheme:
}
"http",
fmt.Sprintf("%s:%d", p.Host.IP, p.Host.DownloadPort),
fmt.Sprintf("download/%s/%s", p.Task.ID[:3], p.Task.ID),
Host:
Path:
RawQuery: fmt.Sprintf("peerId=%s", p.ID),
```

A network-level attacker who cannot join a peer-to-peer network performs a Man-in-the-Middle attack on peers. The adversary can do this because peers (partially) communicate over plaintext HTTP protocol. The attack chains this vulnerability with the one described in TOB-DF2-15 to replace correct files with malicious ones. Unconscious peers use the malicious files.

### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-mcvp-rpgg-9273
- https://nvd.nist.gov/vuln/detail/CVE-2025-59410
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3974
