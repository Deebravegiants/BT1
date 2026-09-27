# [M] Tapir allows DeployKey exposure

## Summary
Severity: Medium
Advisory: CVE-2024-56802
Aliases: GHSA-rj9m-qf65-f5gg
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-12-31
Source: https://osv.dev/vulnerability/CVE-2024-56802
Type: osv

## Details
Tapir is a private Terraform registry. Tapir versions 0.9.0 and 0.9.1 are facing a critical issue with scope-able Deploykeys where attackers can guess the key to get write access to the registry.  User must upgrade to 0.9.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56802.json
- https://github.com/PacoVK/tapir/security/advisories/GHSA-rj9m-qf65-f5gg
- https://nvd.nist.gov/vuln/detail/CVE-2024-56802
- https://github.com/PacoVK/tapir/commit/c36360b611fa0ba4f5e250fa43ecf8a294785a03
