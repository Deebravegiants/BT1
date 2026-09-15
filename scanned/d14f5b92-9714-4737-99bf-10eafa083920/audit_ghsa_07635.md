# [C] Navidrome affected by Denial of Service and disk exhaustion via oversized `size` parameter in `/rest/getCoverArt` and `/share/img/<token>` endpoints

## Summary
Severity: Critical
Advisory: GHSA-hrr4-3wgr-68x3
CVE: CVE-2026-25579
CWE: CWE-400, CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-hrr4-3wgr-68x3
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0 <0.60.0

## Details
### Summary
Authenticated users can crash the Navidrome server by supplying an excessively large `size` parameter to `/rest/getCoverArt` or to a shared-image URL (`/share/img/<token>`). When processing such requests, the server attempts to create an extremely large resized image, causing uncontrolled memory growth. This triggers the Linux OOM killer, terminates the Navidrome process, and results in a full service outage.

If the system has sufficient memory and survives the allocation, Navidrome then writes these extremely large resized images into its cache directory, allowing an attacker to rapidly exhaust server disk space as well.

### Details
Both `/rest/getCoverArt` and `/share/img/<token>` accept a `size` parameter that is passed directly into the image processing routine without any upper bound validation. When a very large integer is provided, Navidrome attempts to generate a resized image of that size. This leads to excessive memory allocation inside the image resizing path.

In the `/rest/getCoverArt` handler, the value is read as:

```go
size := p.IntOr("size", 0)
imgReader, lastUpdate, err := api.artwork.GetOrPlaceholder(ctx, id, size, square)
```

Because no limit is enforced, the image subsystem receives the supplied value as-is. When the requested size is extremely large, the process consumes large amounts of RAM until it is killed by the kernel's OOM killer. If the system has enough available memory to complete the resize operation, the resulting oversized image is then written to Navidrome's cache directory, which can quickly fill the server's disk.

The same behavior is reachable through `/share/img/<token>` as long as the attacker possesses a valid sharing token.

### PoC
1. Authenticate normally to obtain access to `/rest/getCoverArt` or a valid sharing link containing a `/share/img/<token>` URL.
2. Send a regular request with a small size value, for example:

```
/rest/getCoverArt?...&size=300&square=true
```

3. Replace the `size` parameter with a very large number, such as:

```
/rest/getCoverArt?...&size=300000&square=true
```

4. The server rapidly allocates memory while attempting to create an oversized image. This leads to the Navidrome process being terminated by the OOM killer.
5. The same behavior can be reproduced with a valid shared-image link:

```
/share/img/<token>?size=300000&square=true
```

If the system does not run out of memory, the oversized resized image is written to the cache directory, causing disk usage to grow quickly.

### Impact
Supplying an excessively large `size` parameter to `/rest/getCoverArt` or `/share/img/<token>` allows any authenticated user to trigger a Denial of Service condition. During image resizing, the server attempts to allocate extremely large amounts of memory, which can cause not only Navidrome itself to be terminated by the OOM killer, but in some configurations may also destabilize or crash the entire host system.

On systems with sufficient memory, the oversized resized images are written to Navidrome's cache directory instead, allowing an attacker to rapidly consume all available disk space. This leads to a second form of Denial of Service, where the host becomes unable to write logs, operate dependent services, or perform basic system tasks due to storage exhaustion.

## References
- https://github.com/navidrome/navidrome/security/advisories/GHSA-hrr4-3wgr-68x3
- https://nvd.nist.gov/vuln/detail/CVE-2026-25579
- https://github.com/navidrome/navidrome
- https://github.com/navidrome/navidrome/releases/tag/v0.60.0
