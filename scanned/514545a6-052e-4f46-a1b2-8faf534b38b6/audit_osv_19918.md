# [C] CVE-2021-27886

## Summary
Severity: Critical
Advisory: CVE-2021-27886
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-02
Source: https://osv.dev/vulnerability/CVE-2021-27886
Type: osv

## Details
rakibtg Docker Dashboard before 2021-02-28 allows command injection in backend/utilities/terminal.js via shell metacharacters in the command parameter of an API request. NOTE: this is NOT a Docker, Inc. product.

## References
- http://packetstormsecurity.com/files/163416/Docker-Dashboard-Remote-Command-Execution.html
- https://github.com/rakibtg/docker-web-gui/issues/23
- https://www.docker.com/legal/trademark-guidelines
- https://github.com/rakibtg/docker-web-gui/commit/79cdc41809f2030fce21a1109898bd79e4190661
