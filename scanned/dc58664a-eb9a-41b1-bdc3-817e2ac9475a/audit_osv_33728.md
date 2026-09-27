# [H] Nomad Vulnerable To Incorrect ACL Policy Lookup Attached To A Job

## Summary
Severity: High
Advisory: CVE-2025-4922
Aliases: GHSA-rx97-6c62-55mf, GO-2025-3758
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2025-06-11
Source: https://osv.dev/vulnerability/CVE-2025-4922
Type: osv

## Details
Nomad Community and Nomad Enterprise (“Nomad”) prefix-based ACL policy lookup can lead to incorrect rule application and shadowing. This vulnerability, identified as CVE-2025-4922, is fixed in Nomad Community Edition 1.10.2 and Nomad Enterprise 1.10.2, 1.9.10, and 1.8.14.

## References
- https://discuss.hashicorp.com/t/hcsec-2025-12-nomad-vulnerable-to-incorrect-acl-policy-lookup-attached-to-a-job/75396
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4922.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4922
- https://github.com/hashicorp/nomad
