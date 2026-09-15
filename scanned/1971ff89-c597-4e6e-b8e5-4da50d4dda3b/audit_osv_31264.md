# [C] Puppet-foreman: an authentication bypass vulnerability exists in foreman

## Summary
Severity: Critical
Advisory: CVE-2024-7012
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-7012
Type: osv

## Details
An authentication bypass vulnerability has been identified in Foreman when deployed with External Authentication, due to the puppet-foreman configuration. This issue arises from Apache's mod_proxy not properly unsetting headers because of restrictions on underscores in HTTP headers, allowing authentication through a malformed header. This flaw impacts all active Satellite deployments (6.13, 6.14 and 6.15) and could potentially enable unauthorized users to gain administrative access.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2024:6335
- https://access.redhat.com/errata/RHSA-2024:6336
- https://access.redhat.com/errata/RHSA-2024:6337
- https://access.redhat.com/errata/RHSA-2024:8906
- https://access.redhat.com/security/cve/CVE-2024-7012
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7012.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7012
- https://bugzilla.redhat.com/show_bug.cgi?id=2299429
- https://github.com/theforeman/puppet-foreman
