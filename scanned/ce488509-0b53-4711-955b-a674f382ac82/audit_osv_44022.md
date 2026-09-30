# [M] Infinite Image Browsing Resolves Paths With normpath, Allowing Symlink Escape From Scanned Directories

## Summary
Severity: Medium
Advisory: CVE-2026-77815
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77815
Type: osv

## Details
to_abs_path in scripts/iib/tool.py normalised the requested path with os.path.normpath, which collapses dot segments but does not resolve symbolic links. A symlink placed inside a scanned directory therefore satisfies the containment comparison performed by is_path_trusted in scripts/iib/api.py while pointing outside that directory, and FileResponse follows the link when serving the response, so a link created in an image directory and targeting a file such as /etc/passwd discloses that file. Whether the check applies depends on get_enable_access_control in scripts/iib/tool.py: it returns true when IIB_ACCESS_CONTROL is set to enable, false when set to disable, and otherwise true when the host Stable Diffusion WebUI was started with share, ngrok, listen or server_name, falling back to false. Confinement is therefore active in the network-exposed WebUI deployments that rely on it, while a standalone run with no such option serves every readable file regardless of this flaw. The fix resolves the path with os.path.realpath.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77815.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77815
- https://www.vulncheck.com/advisories/infinite-image-browsing-resolves-paths-with-normpath-allowing-symlink-escape-from-scanned-directories
- https://github.com/zanllp/infinite-image-browsing/issues/968
- https://github.com/zanllp/infinite-image-browsing/pull/969
- https://github.com/zanllp/infinite-image-browsing/commit/4057a624c7a23a36f0b4dc6a545b40767d602450
- https://github.com/zanllp/infinite-image-browsing
- https://github.com/zanllp/infinite-image-browsing/blob/v1.8.0/scripts/iib/api.py#L329-L344
- https://github.com/zanllp/infinite-image-browsing/blob/v1.8.0/scripts/iib/tool.py#L172-L175
