# [M] PPTAgent: Arbitrary File Write + Directory Creation via markdown_table_to_image

## Summary
Severity: Medium
Advisory: GHSA-hrcw-xc63-g29m
CVE: CVE-2026-42078
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-hrcw-xc63-g29m
Type: github-advisory

## Affected
- PyPI: `pptagent` — affected >=0 <1.1.36

## Details
### Summary

The `markdown_table_to_image` tool accepts a caller-controlled path parameter and passes it directly to `get_html_table_image`:

```python
# pptagent/mcp_server.py:127-143
def markdown_table_to_image(markdown_table: str, path: str, css: str) -> str:
    """
    Args:
        path (str): The file path where the image will be saved
    """
    html = markdown_to_html(markdown_table)
    get_html_table_image(html, path, css)           # ← no path validation
    return f"Markdown table converted to image and saved to {path}"

# pptagent/utils.py:337-366
def get_html_table_image(html: str, output_path: str, css: str = None):
    parent_dir, base_name = os.path.split(output_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir)                     # ← creates arbitrary directories
    hti = Html2Image(...)
    hti.screenshot(
        html_str=html,
        css_str=css,
        save_as=base_name,                          # ← writes image to any directory
        size=(1000, 600),
    )
```

`os.makedirs(parent_dir)` creates arbitrary directory trees, and `Html2Image.screenshot` writes the rendered image to `parent_dir/base_name`. Unlike `download_file` in the same project, there is no `is_relative_to(workspace)` guard. This behaviour can be fixed with the same pattern as the above.


### Impact

The concrete attack scenarios include

- SSH key replacement: `path = "/home/user/.ssh/authorized_keys"` — replaces the authorized_keys file with an image binary (breaks - SSH but could be an image crafted with a specific PNG/JPEG payload).
- Web shell: `path = "/var/www/html/uploads/shell.php"` — writes the rendered PNG there; the file has the .php extension but PNG content; combined with Apache Options +MultiViews or file-include vulnerabilities could be dangerous.
- Directory creation oracle: `path = "/root/test/probe.png"` — if the directory is created, confirms the target path exists; if it errors, reveals permissions information.

## References
- https://github.com/icip-cas/PPTAgent/security/advisories/GHSA-hrcw-xc63-g29m
- https://nvd.nist.gov/vuln/detail/CVE-2026-42078
- https://github.com/icip-cas/PPTAgent/commit/418491a9a1c02d9d93194b5973bb58df35cf9d00
- https://github.com/icip-cas/PPTAgent
