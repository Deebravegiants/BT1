# [C] CyberPanel 2.4.3 Authenticated RCE via Remote Backup Feature

## Summary
Severity: Critical
Advisory: CVE-2026-71965
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-71965
Type: osv

## Details
CyberPanel 2.4.3, fixed in commit eca0c3c, contains an authenticated remote code execution vulnerability in the remote backup feature that allows authenticated attackers to gain root-level SSH access by supplying a malicious remote server address. Attackers can exploit the unverified SSH public key retrieval process to write an attacker-controlled public key directly to /root/.ssh/authorized_keys, granting persistent root access to the host system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71965.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71965
- https://www.vulncheck.com/advisories/cyberpanel-authenticated-rce-via-remote-backup-feature
- https://github.com/usmannasir/cyberpanel/commit/eca0c3cbeb35af8eaae9fafb094e8ef3cd923643
- https://github.com/usmannasir/cyberpanel
- https://themcsam.github.io/posts/cyberpanel-2.4.3-vulnerabilties/
