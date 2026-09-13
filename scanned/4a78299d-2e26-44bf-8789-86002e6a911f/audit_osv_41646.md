# [C] Incus has an argument injection in storage volume block.create_options that leads to arbitrary command execution

## Summary
Severity: Critical
Advisory: CVE-2026-62867
Aliases: GHSA-q7xw-r4w2-2wcm
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-62867
Type: osv

## Details
Incus is a system container and virtual machine manager. Prior to version 7.3.0, improper validation of user-provided `block.create_options` in storage volume configuration leads to argument injection in the constructed filesystem creation command line. This allows a project-scoped user to inject arbitrary arguments into the binary executed as root. Version 7.3.0 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62867.json
- https://github.com/lxc/incus/security/advisories/GHSA-q7xw-r4w2-2wcm
- https://nvd.nist.gov/vuln/detail/CVE-2026-62867
