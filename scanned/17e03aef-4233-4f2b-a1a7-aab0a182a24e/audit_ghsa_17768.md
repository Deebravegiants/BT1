# [C] Gradio Blocked Path ACL Bypass Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-j2jg-fq62-7c3h
CVE: CVE-2025-23042
CWE: CWE-178, CWE-285
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-01-14
Source: https://github.com/advisories/GHSA-j2jg-fq62-7c3h
Type: github-advisory

## Affected
- PyPI: `gradio` — affected >=0 <5.11.0

## Details
## Summary

Gradio's Access Control List (ACL) for file paths can be bypassed by altering the letter case of a blocked file or directory path. This vulnerability arises due to the lack of case normalization in the file path validation logic. On case-insensitive file systems, such as those used by Windows and macOS, this flaw enables attackers to circumvent security restrictions and access sensitive files that should be protected.

This issue can lead to unauthorized data access, exposing sensitive information and undermining the integrity of Gradio's security model. Given Gradio's popularity for building web applications, particularly in machine learning and AI, this vulnerability may pose a substantial threat if exploited in production environments.

## Affected Version

Gradio <= 5.6.0

## Impact

- **Unauthorized Access**: Sensitive files or directories specified in `blocked_paths` can be accessed by attackers.

- **Data Exposure**: Critical files, such as configuration files or user data, may be leaked.

- **Security Breach**: This can lead to broader application or system compromise if sensitive files contain credentials or API keys.

## Root Cause

The [`blocked_paths`](https://github.com/gradio-app/gradio/blob/main/gradio/blocks.py#L2310) parameter in Gradio block's initial configuration is designed to restrict user access to specific files or directories in the local file system. However, it does not account for case-insensitive operating systems, such as Windows and macOS. This oversight enables attackers to bypass ACL restrictions by changing the case of file paths.

Vulnerable snippet: 

```python
# https://github.com/gradio-app/gradio/blob/main/gradio/utils.py#L1500-L1517
def is_allowed_file(
    path: Path,
    blocked_paths: Sequence[str | Path],
    allowed_paths: Sequence[str | Path],
    created_paths: Sequence[str | Path],
) -> tuple[
    bool, Literal["in_blocklist", "allowed", "created", "not_created_or_allowed"]
]:
    in_blocklist = any(
        is_in_or_equal(path, blocked_path) for blocked_path in blocked_paths
    )
    if in_blocklist:
        return False, "in_blocklist"
    if any(is_in_or_equal(path, allowed_path) for allowed_path in allowed_paths):
        return True, "allowed"
    if any(is_in_or_equal(path, created_path) for created_path in created_paths):
        return True, "created"
    return False, "not_created_or_allowed"
```

Gradio relies on `is_in_or_equal` to determine if a file path is restricted. However, this logic fails to handle case variations in paths on case-insensitive file systems, leading to the bypass.

## Proof of Concept (PoC)

### Steps to Reproduce

- Deploy a Gradio demo app on a case-insensitive operating system (e.g., Windows or macOS).

  ```bash
  import gradio as gr
  def update(name):
      return f"Welcome to Gradio, {name}!"
  
  with gr.Blocks() as demo:
      gr.Markdown("Start typing below and then click **Run** to see the output.")
      with gr.Row():
          inp = gr.Textbox(placeholder="What is your name?")
          out = gr.Textbox()
      btn = gr.Button("Run")
      btn.click(fn=update, inputs=inp, outputs=out)
  
  demo.launch(blocked_paths=['resources/admin'], allowed_paths=['resources/'])
  ```

- Set up the file system:

  - Create a folder named `resources` in the same directory as the app, containing a file `1.txt`.

  - Inside the `resources` folder, create a subfolder named `admin` containing a sensitive file `credential.txt` (this file should be inaccessible due to `blocked_paths`).

- Perform the attack:

  - Access the sensitive file using a case-altered path:

    ```
    http://127.0.0.1:PORT/gradio_api/file=resources/adMin/credential.txt
    ```

### Expected Result

Access to `resources/admin/credential.txt` should be blocked.

### Actual Result

By altering the case in the path (e.g., `adMin`), the blocked ACL is bypassed, and unauthorized access to the sensitive file is granted.

![image-20241119172439042](https://api.2h0ng.wiki:443/noteimages/2024/11/19/17-24-39-883969d4c31ce8a8d2a939654fab56d4.png)

This demonstration highlights that flipping the case of restricted paths allows attackers to bypass Gradio's ACL and access sensitive data.

## Remediation Recommendations

1. **Normalize Path Case**:

   - Before evaluating paths against the ACL, normalize the case of both the requested path and the blocked paths (e.g., convert all paths to lowercase).

   - Example:

     ```python
     normalized_path = str(path).lower()
     normalized_blocked_paths = [str(p).lower() for p in blocked_paths]
     ```

2. **Update Documentation**:

   - Warn developers about potential risks when deploying Gradio on case-insensitive file systems.

3. **Release Security Patches**:

   - Notify users of the vulnerability and release an updated version of Gradio with the fixed logic.

##

## References
- https://github.com/gradio-app/gradio/security/advisories/GHSA-j2jg-fq62-7c3h
- https://nvd.nist.gov/vuln/detail/CVE-2025-23042
- https://github.com/gradio-app/gradio/commit/6b63fdec441b5c9bf910f910a2505d8defbb6bf8
- https://github.com/gradio-app/gradio
- https://github.com/gradio-app/gradio/releases/tag/gradio%405.11.0
- https://github.com/pypa/advisory-database/tree/main/vulns/gradio/PYSEC-2025-118.yaml
