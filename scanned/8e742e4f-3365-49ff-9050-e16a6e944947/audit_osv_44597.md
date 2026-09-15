# [M] Pcs: pcs: non-root haclient users can read arbitrary files via pcs host auth --token

## Summary
Severity: Medium
Advisory: CVE-2026-84828
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-84828
Type: osv

## Details
A flaw was found in PCS (Pacemaker Configuration System). A local attacker with membership in the 'haclient' group can exploit the 'pcs host auth --token' command to read the contents of arbitrary files on the filesystem, provided the files are shorter than 256 bytes. The file contents are read with root privileges by the pcsd daemon and can be exfiltrated by the attacker through subsequent cluster node communication. This allows disclosure of sensitive data such as API keys, tokens, or configuration secrets that would otherwise be inaccessible to the attacker.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-84828
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84828.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84828
- https://bugzilla.redhat.com/show_bug.cgi?id=2527320
- https://github.com/ClusterLabs/pcs/commit/9178b78d11baa70e700a5c0d9fc1c17f27d452fa
