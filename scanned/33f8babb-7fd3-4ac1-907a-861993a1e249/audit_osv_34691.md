# [H] CVE-2025-63916

## Summary
Severity: High
Advisory: CVE-2025-63916
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-11-17
Source: https://osv.dev/vulnerability/CVE-2025-63916
Type: osv

## Details
MyScreenTools v2.2.1.0 contains a critical OS command injection vulnerability in the GIF compression tool. The application fails to properly sanitize user-supplied file paths before passing them to cmd.exe, allowing attackers to execute arbitrary system commands with the privileges of the user running the application. The vulnerability exists in the CMD() function within GIFSicleTool\Form_gif_sicle_tool.cs, which constructs shell commands by concatenating unsanitized user input (file paths) and executes them via cmd.exe.

## References
- https://github.com/cydtseng/Vulnerability-Research/blob/main/myscreentools/OSCommandInjection-GifCompression.md
- https://github.com/luotengyuan/MyScreenTools/blob/master/GIFSicleTool/Form_gif_sicle_tool.cs
- https://github.com/luotengyuan/MyScreenTools/tree/master
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63916.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63916
