# [C] CVE-2021-30503

## Summary
Severity: Critical
Advisory: CVE-2021-30503
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-13
Source: https://osv.dev/vulnerability/CVE-2021-30503
Type: osv

## Details
The unofficial GLSL Linting extension before 1.4.0 for Visual Studio Code allows remote code execution via a crafted glslangValidatorPath in the workspace configuration.

## References
- https://marketplace.visualstudio.com/items/CADENAS.vscode-glsllint/changelog#:~:text=1.4.x
- https://vuln.ryotak.me/advisories/27
- https://github.com/hsimpson/vscode-glsllint/commit/3effba525bdff7d4257e66a6815ff956d2bce8ac
