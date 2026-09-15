# [M] P11-kit: null dereference via c_derivekey with specific null parameters

## Summary
Severity: Medium
Advisory: CVE-2026-2100
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-2100
Type: osv

## Details
A flaw was found in p11-kit. A remote attacker could exploit this vulnerability by calling the C_DeriveKey function on a remote token with specific IBM kyber or IBM btc derive mechanism parameters set to NULL. This could lead to the RPC-client attempting to return an uninitialized value, potentially resulting in a NULL dereference or undefined behavior. This issue may cause an application level denial of service or other unpredictable system states.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://github.com/p11-glue/p11-kit/releases/tag/0.26.2
- https://access.redhat.com/errata/RHSA-2026:18143
- https://access.redhat.com/errata/RHSA-2026:18599
- https://access.redhat.com/errata/RHSA-2026:21275
- https://access.redhat.com/errata/RHSA-2026:22634
- https://access.redhat.com/errata/RHSA-2026:27998
- https://access.redhat.com/errata/RHSA-2026:58981
- https://access.redhat.com/errata/RHSA-2026:7065
- https://access.redhat.com/security/cve/CVE-2026-2100
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2100.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2100
- https://bugzilla.redhat.com/show_bug.cgi?id=2437308
- https://github.com/p11-glue/p11-kit/pull/740
- https://github.com/p11-glue/p11-kit
