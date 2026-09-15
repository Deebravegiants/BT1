# [M] Wazuh: RBAC permission-effect check in mask_sensitive_config allows low-privilege users to read cluster.key

## Summary
Severity: Medium
Advisory: CVE-2026-61783
Aliases: GHSA-vjcq-cf36-f5gx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-61783
Type: osv

## Details
Wazuh is an open-source security platform providing unified XDR and SIEM protection for endpoints and cloud workloads. In versions 4.14.0 through 4.14.6, an authenticated low-privilege user can read the cluster secret from the manager configuration because the logic that masks sensitive values is disabled by any update-config RBAC rule, including an explicit deny. The mask_sensitive_config() decorator applies masking only when _has_update_permissions() returns false, but that gate treats a user as able to update the config whenever a  manager:update_config  or  cluster:update_config  rule exists, without ever checking whether the rule's effect is allow or deny. Because a deny rule is stored as a real entry, a read-only account that is hardened by explicitly denying config edits is counted as having update permission, which turns masking off. A single authenticated GET request to the configuration endpoint with  raw=true  then returns the verbatim ossec.conf XML with  cluster.key  in clear, whereas an otherwise identical account without the deny rule sees the value masked. This issue is fixed in version 4.14.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61783.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-vjcq-cf36-f5gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-61783
- https://github.com/wazuh/wazuh/commit/939f2e52afff8fbeb7b0894f3f1417eb6c395db3
