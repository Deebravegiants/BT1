# [C] hulumi before v1.3.2 SCP Template Tag-on-Create Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-82859
Aliases: GHSA-86q4-r5j3-ff5c
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82859
Type: osv

## Details
hulumi versions before v1.3.2 contain a deployment SCP template that allows tag-on-create bypasses for hulumi:iac-role protections. Attackers can bypass intended IAM boundary restrictions by exploiting the weakened SCP template in downstream deployments.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82859.json
- https://github.com/kerberosmansour/hulumi/security/advisories/GHSA-86q4-r5j3-ff5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-82859
- https://www.vulncheck.com/advisories/hulumi-before-1.3.2-scp-template-tag-on-create-bypass
