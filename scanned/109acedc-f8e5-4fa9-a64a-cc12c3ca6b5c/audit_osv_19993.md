# [C] CVE-2021-28967

## Summary
Severity: Critical
Advisory: CVE-2021-28967
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-24
Source: https://osv.dev/vulnerability/CVE-2021-28967
Type: osv

## Details
The unofficial MATLAB extension before 2.0.1 for Visual Studio Code allows attackers to execute arbitrary code via a crafted workspace because of lint configuration settings.

## References
- https://github.com/Gimly/vscode-matlab/releases
- https://marketplace.visualstudio.com/items/Gimly81.matlab/changelog
- https://vuln.ryotak.me/advisories/2
- https://github.com/Gimly/vscode-matlab/commit/fc5dc53397677464099e80629e785a25718bf5ec
