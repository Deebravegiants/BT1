# [M] Zmarkdown Server-Side Request Forgery (SSRF) in remark-download-images

## Summary
Severity: Medium
Advisory: GHSA-mf74-qq7w-6j7v
Ecosystem: npm
Published: 2024-02-03
Source: https://github.com/advisories/GHSA-mf74-qq7w-6j7v
Type: github-advisory

## Affected
- npm: `remark-images-download` — affected >=0 <3.1.0

## Details
### Impact

A major blind SSRF has been found in `remark-images-download`, which allowed
for requests to be made to neighboring servers on local IP ranges.
The issue came from a loose filtering of URLs inside the module.

Imagine a server running on a private network `192.168.1.0/24`.
A private service serving images is running on `192.168.1.2`, and
is not expected to be accessed by users. A machine is running
`remark-images-download` on the neighboring `192.168.1.3` host.
An user enters the following Markdown:

```markdown
![](http://192.168.1.2/private-img.png)
```

The image is downloaded by the server and included inside the resulting
document. Hence, the user has access to the private image.

It has been corrected by preventing images downloads from
local IP ranges, both in IPv4 and IPv6.
To avoid malicious domain names, resolved local IPs from are also
forbidden inside the module.
This vulnerability impact is moderate, as it is can allow access to
unexposed documents on the local network, and is very easy
to exploit.

### Patches

The vulnerability has been patched in version 3.1.0.
If impacted, you should update to this version as soon as possible.

Please note that a minor version has been released instead of a bugfix.
This is due to a new option included to prevent another vulnerability,
upgrading to the new version will not break compatibility.

### Workarounds

No workaround is known, the package should be upgraded.

### For more information

If you have any questions or comments about this advisory, open an issue in [ZMarkdown](https://github.com/zestedesavoir/zmarkdown/issues).

## References
- https://github.com/zestedesavoir/zmarkdown/security/advisories/GHSA-mf74-qq7w-6j7v
- https://github.com/zestedesavoir/zmarkdown
