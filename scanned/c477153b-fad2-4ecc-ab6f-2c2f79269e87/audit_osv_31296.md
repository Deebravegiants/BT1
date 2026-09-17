# [H] CVE-2024-8038

## Summary
Severity: High
Advisory: CVE-2024-8038
Aliases: GHSA-xwgj-vpm9-q2rq, GO-2024-3175
CVSS: 7.9 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:H)
Published: 2024-10-02
Source: https://osv.dev/vulnerability/CVE-2024-8038
Type: osv

## Details
Vulnerable juju introspection abstract UNIX domain socket. An abstract UNIX domain socket responsible for introspection is available without authentication locally to network namespace users. This enables denial of service attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8038.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8038
- https://github.com/juju/juju/security/advisories/GHSA-xwgj-vpm9-q2rq
- https://www.cve.org/CVERecord?id=CVE-2024-8038
- https://github.com/juju/juju
