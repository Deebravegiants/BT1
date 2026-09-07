# [M] Gogs XSS allowed by stored call in PDF renderer

## Summary
Severity: Medium
Advisory: GHSA-xh32-cx6c-cp4v
CVE: CVE-2025-47943
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2025-06-26
Source: https://github.com/advisories/GHSA-xh32-cx6c-cp4v
Type: github-advisory

## Affected
- Go: `github.com/gogs/gogs` — affected >=0 <0.13.3-0.20250608224432-110117b2e5e5
- Go: `gogs.io/gogs` — affected >=0 <0.13.3-0.20250608224432-110117b2e5e5

## Details
### Summary

A stored XSS is present in Gogs which allows client-side Javascript code execution.

### Details

Gogs Version:
```
docker images
REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
gogs/gogs    latest    fe92583bc4fe   10 hours ago   99.3MB
```

Application version: `0.14.0+dev`

Local setup using:
```bash
# Pull image from Docker Hub.
docker pull gogs/gogs

# Create local directory for volume.
sudo mkdir -p /var/gogs

# Use `docker run` for the first time.
docker run --name=gogs -p 10022:22 -p 10880:3000 -v /var/gogs:/data gogs/gogs
```

The vulnerability is caused by the usage of a vulnerable and outdated component: `pdfjs-1.4.20` under public/plugins/.  
Read more about this vulnerability at [codeanlabs - CVE-2024-4367](https://codeanlabs.com/blog/research/cve-2024-4367-arbitrary-js-execution-in-pdf-js/).

### PoC

1. Upload the Proof of Concept file hosted at https://codeanlabs.com/wp-content/uploads/2024/05/poc_generalized_CVE-2024-4367.pdf in a repository.
2. Click on the file to be previewed.

![poc](https://github.com/user-attachments/assets/5af1303e-8751-49c8-af2e-d0631dd18957)


### Credits

Edoardo Ottavianelli

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-xh32-cx6c-cp4v
- https://nvd.nist.gov/vuln/detail/CVE-2025-47943
- https://github.com/gogs/gogs/commit/110117b2e5e5baa4809c819bec701e929d2d8d40
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.13.3
- https://www.hacktivesecurity.com/blog/2025/07/15/cve-2025-47943-stored-xss-in-gogs-via-pdf
