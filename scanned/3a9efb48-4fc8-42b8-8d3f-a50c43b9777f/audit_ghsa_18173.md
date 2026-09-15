# [H] Dragonfly vulnerable to server-side request forgery

## Summary
Severity: High
Advisory: GHSA-g2rq-jv54-wcpr
CVE: CVE-2025-59346
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-g2rq-jv54-wcpr
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
There are multiple server-side request forgery (SSRF) vulnerabilities in the DragonFly2 system. The vulnerabilities enable users to force DragonFly2’s components to make requests to internal services, which otherwise are not accessible to the users.
One SSRF attack vector is exposed by the Manager’s API. The API allows users to create jobs. When creating a Preheat type of a job, users provide a URL that the Manager connects to (see figures 2.1–2.3). The URL is weakly validated, and so users can trick the Manager into sending HTTP requests to services that are in the Manager’s local network.

```golang
func (p *preheat) CreatePreheat(ctx context.Context, schedulers []models.Scheduler,
json types.PreheatArgs) (*internaljob.GroupJobState, error) {
[skipped]
       url := json.URL
[skipped]
       // Generate download files
       var files []internaljob.PreheatRequest
       switch PreheatType(json.Type) {
       case PreheatImageType:
             // Parse image manifest url
skipped, err := parseAccessURL(url) [skipped]
[skipped]
case PreheatFileType: [skipped]
}
```

A second attack vector is in peer-to-peer communication. A peer can ask another peer to make a request to an arbitrary URL by triggering the pieceManager.DownloadSource method (figure 2.4), which calls the httpSourceClient.GetMetadata method, which performs the request.

Another attack vector is due to the fact that HTTP clients used by the DragonFly2’s components do not disable support for HTTP redirects. This configuration means that an HTTP request sent to a malicious server may be redirected by the server to a component’s internal service.

### Patches
- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-g2rq-jv54-wcpr
- https://nvd.nist.gov/vuln/detail/CVE-2025-59346
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3968
