# [H] Arbitrary file read+write on host via templates/ symlink in malicious image

## Summary
Severity: High
Advisory: CVE-2026-16033
Aliases: GHSA-9hcm-hxh5-7xxh
CVSS: 8.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-16033
Type: osv

## Details
A path traversal vulnerability in LXD allows an attacker to achieve arbitrary host file read or unconstrained file creation. When processing image metadata templates, LXD fails to properly sanitize or restrict template file paths from escaping the instance templates directory (specifically affecting virtual machine / QEMU driver execution paths). An attacker can exploit this flaw by providing a crafted image archive with malicious template directives containing path traversal sequences, causing LXD to access or write files outside the intended template directory on the host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/16xxx/CVE-2026-16033.json
- https://github.com/canonical/lxd/security/advisories/GHSA-9hcm-hxh5-7xxh
- https://nvd.nist.gov/vuln/detail/CVE-2026-16033
- https://github.com/canonical/lxd
