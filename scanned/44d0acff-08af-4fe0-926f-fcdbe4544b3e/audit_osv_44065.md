# [H] Improper Limitation of a Pathname to a Restricted Directory in Kibana Leading to Unauthorized Deletion of Privileged Resources

## Summary
Severity: High
Advisory: CVE-2026-78590
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-78590
Type: osv

## Details
Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') (CWE-22) in the Kibana Fleet feature can lead to the unauthorized deletion of privileged resources via Path Traversal (CAPEC-126). A low-privileged user holding Fleet Settings write access could cause a subsequent administrative action to act on unintended internal resources, resulting in the deletion of privileged resources such as user accounts and other organizational assets. Exploitation requires an administrator to interact with the affected Fleet interface.

## References
- https://discuss.elastic.co/t/kibana-8-19-18-9-3-6-9-4-3-security-update-esa-2026-158/390113
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78590.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78590
