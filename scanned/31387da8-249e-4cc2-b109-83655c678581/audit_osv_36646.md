# [H] Podman Desktop Extension System Vulnerable to Authentication Bypass

## Summary
Severity: High
Advisory: CVE-2026-24835
Aliases: GHSA-v3fx-qg34-6g9m
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-28
Source: https://osv.dev/vulnerability/CVE-2026-24835
Type: osv

## Details
Podman Desktop is a graphical tool for developing on containers and Kubernetes. A critical authentication bypass vulnerability in Podman Desktop prior to version 1.25.1 allows any extension to completely circumvent permission checks and gain unauthorized access to all authentication sessions. The `isAccessAllowed()` function unconditionally returns `true`, enabling malicious extensions to impersonate any user, hijack authentication sessions, and access sensitive resources without authorization. This vulnerability affects all versions of Podman Desktop. Version 1.25.1 contains a patch for the issue.

## References
- https://drive.google.com/file/d/1ib4RG34mGHDlXeyib8L2j9L5rEDxuDM5/view?usp=sharing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24835.json
- https://github.com/podman-desktop/podman-desktop/security/advisories/GHSA-v3fx-qg34-6g9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-24835
