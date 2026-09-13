# [H] Arbitrary code execution through yaml global parameters

## Summary
Severity: High
Advisory: CVE-2023-0462
CVSS: 8.0 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-09-20
Source: https://osv.dev/vulnerability/CVE-2023-0462
Type: osv

## Details
An arbitrary code execution flaw was found in Foreman. This issue may allow an admin user to execute arbitrary code on the underlying operating system by setting global parameters with a YAML payload.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2023-0462
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0462.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0462
- https://bugzilla.redhat.com/show_bug.cgi?id=2162970
