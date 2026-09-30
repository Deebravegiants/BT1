# [M] Infinite Image Browsing is_path_trusted Prefix Comparison Omits the Trailing Path Separator

## Summary
Severity: Medium
Advisory: CVE-2026-77814
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77814
Type: osv

## Details
is_path_trusted in scripts/iib/api.py compares the requested path against each allowed parent directory with path.startswith(parent_path), without appending a path separator. A directory whose name merely begins with an allowed path therefore satisfies the comparison, so where /data/images is allowed a request for /data/images_private/secret.txt is treated as trusted and served by FileResponse, disclosing files the confinement was meant to exclude. Whether the check applies depends on get_enable_access_control in scripts/iib/tool.py: it returns true when IIB_ACCESS_CONTROL is set to enable, false when set to disable, and otherwise true when the host Stable Diffusion WebUI was started with share, ngrok, listen or server_name, falling back to false. Confinement is therefore active in the network-exposed WebUI deployments that rely on it, while a standalone run with no such option serves every readable file regardless of this flaw. The fix compares against parent_path joined with os.sep.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77814.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-77814
- https://www.vulncheck.com/advisories/infinite-image-browsing-is-path-trusted-prefix-comparison-omits-the-trailing-path-separator
- https://github.com/zanllp/infinite-image-browsing/issues/968
- https://github.com/zanllp/infinite-image-browsing/pull/969
- https://github.com/zanllp/infinite-image-browsing/commit/4057a624c7a23a36f0b4dc6a545b40767d602450
- https://github.com/zanllp/infinite-image-browsing
- https://github.com/zanllp/infinite-image-browsing/blob/v1.8.0/scripts/iib/api.py#L329-L344
