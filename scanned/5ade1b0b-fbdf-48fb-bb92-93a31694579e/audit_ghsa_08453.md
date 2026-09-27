# [M] PPTAgent: Arbitrary File Write via `save_generated_slides`

## Summary
Severity: Medium
Advisory: GHSA-pxhg-7xr2-w7xg
CVE: CVE-2026-42080
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-pxhg-7xr2-w7xg
Type: github-advisory

## Affected
- PyPI: `pptagent` — affected >=0 <1.1.36

## Details
## Summary

> This vulnerability has been fixed in https://github.com/icip-cas/PPTAgent/commit/418491a9a1c02d9d93194b5973bb58df35cf9d00.

The `save_generated_slides` MCP tool accepts a pptx_path argument and writes the generated PPTX file to that path without any workspace restriction or path validation:

```python
# pptagent/mcp_server.py:288-300
async def save_generated_slides(pptx_path: str):
    """Save the generated slides to a PowerPoint file.

    Args:
        pptx_path: The path to save the PowerPoint file
    """
    pptx = Path(pptx_path)
    assert len(self.slides), (
        "No slides generated, please call `generate_slide` first"
    )
    pptx.parent.mkdir(parents=True, exist_ok=True)   # ← creates arbitrary directories
    self.empty_prs.save(pptx_path)                    # ← writes to arbitrary path
```

The call to `pptx.parent.mkdir(parents=True, exist_ok=True)` creates any intermediate directories, and `self.empty_prs.save(pptx_path)` writes a valid PPTX binary (ZIP archive) to the specified path. No is_relative_to(workspace) check is performed — contrast with download_file in deeppresenter/tools/search.py:290, which correctly enforces workspace confinement.

The server changes directory to WORKSPACE (if set) on startup, so relative paths land in the workspace. Absolute paths, however, reach any filesystem location accessible to the server process.

## Impact

The concrete attack scenarios include

1. Cron persistence (root-running server): `pptx_path = "/etc/cron.d/backdoor"` → writes a PPTX ZIP to a path the cron daemon reads; if the ZIP header is misinterpreted, this may corrupt cron or be exploitable depending on parser behaviour.
2. Dot-file overwrite: `pptx_path = "/home/user/.bashrc"` → overwrites shell init file with a binary blob containing arbitrary content in the PPTX's embedded comments/custom properties.
3. Directory traversal from workspace: `pptx_path = "../../.ssh/known_hosts.pptx"` → escapes workspace entirely.
4. Denial of service: `pptx_path = "/dev/sda"` writes to a raw device.

## Remediation

The potential fix is something like:

```python
async def save_generated_slides(pptx_path: str):
    workspace = Path(os.getcwd()).resolve()
    target = Path(pptx_path).resolve()
    if not target.is_relative_to(workspace):
        raise ValueError(f"Access denied: path outside workspace: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    self.empty_prs.save(str(target))
```

## References
- https://github.com/icip-cas/PPTAgent/security/advisories/GHSA-pxhg-7xr2-w7xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-42080
- https://github.com/icip-cas/PPTAgent/commit/418491a9a1c02d9d93194b5973bb58df35cf9d00
- https://github.com/icip-cas/PPTAgent
