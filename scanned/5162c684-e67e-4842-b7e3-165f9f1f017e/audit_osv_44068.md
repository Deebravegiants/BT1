# [M] Stored Path Traversal in Kibana Leading to Unauthorized Deletion of Internal Resources

## Summary
Severity: Medium
Advisory: CVE-2026-78599
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-78599
Type: osv

## Details
Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') (CWE-22) in the Kibana Fleet feature can lead to the unauthorized deletion of internal resources via Path Traversal (CAPEC-126). A low-privileged user holding Fleet write access could cause a subsequent administrative delete action to act on unintended internal resources. Exploitation requires an administrator to interact with the affected Fleet interface.

## References
- https://discuss.elastic.co/t/kibana-8-19-18-9-4-3-security-update-esa-2026-157/390112
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78599.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78599
