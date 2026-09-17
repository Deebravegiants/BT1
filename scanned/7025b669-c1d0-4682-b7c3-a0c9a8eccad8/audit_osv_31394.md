# [H] Nomad Vulnerable To Event Stream Namespace ACL Policy Bypass Through Wildcard Namespace

## Summary
Severity: High
Advisory: CVE-2025-0937
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-02-12
Source: https://osv.dev/vulnerability/CVE-2025-0937
Type: osv

## Details
Nomad Community and Nomad Enterprise ("Nomad") event stream configured with a wildcard namespace can bypass the ACL Policy allowing reads on other namespaces.

## References
- https://discuss.hashicorp.com/t/hcsec-2025-02-nomad-vulnerable-to-event-stream-namespace-acl-policy-bypass-through-wildcard-namespace/73191
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0937.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0937
- https://github.com/hashicorp/nomad
