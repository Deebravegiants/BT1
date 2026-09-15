# [H] Trilium arbitrary file read and denial of service via file:// URLs in the automatic image-download feature

## Summary
Severity: High
Advisory: CVE-2026-53580
Aliases: GHSA-3gxr-j6g6-q75c
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-53580
Type: osv

## Details
Trilium is an open-source hierarchical note-taking application. In versions prior to 0.104.0, the automatic image-download feature accepts file:// URLs in a note's img tags and reads the referenced local file with no path validation, allowing any authenticated user to disclose arbitrary files readable by the Trilium process. When a text note is saved, Trilium scans its HTML for image sources and downloads each external one; because the HTML sanitizer keeps file as an allowed scheme, a source such as file:///etc/passwd is passed straight to a filesystem read and its contents are stored as a note attachment the user can then retrieve. Pointing the same primitive at an unbounded source such as /dev/zero causes uncontrolled memory allocation that crashes the server process. The feature is enabled by default and is reachable through the web UI, the ETAPI, the web clipper, and note imports, requiring only an authenticated session or an ETAPI token. This issue is fixed in version 0.104.0

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53580.json
- https://github.com/TriliumNext/Trilium/security/advisories/GHSA-3gxr-j6g6-q75c
- https://nvd.nist.gov/vuln/detail/CVE-2026-53580
- https://github.com/TriliumNext/Trilium/commit/c417c901dfe45222c321fab1685f26730cc2068f
