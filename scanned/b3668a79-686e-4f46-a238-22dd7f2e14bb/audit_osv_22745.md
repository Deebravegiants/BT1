# [M] CVE-2022-37428

## Summary
Severity: Medium
Advisory: CVE-2022-37428
CVSS: 6.5 (CVSS:3.1/AC:L/AV:N/A:H/C:N/I:N/PR:L/S:U/UI:N)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/CVE-2022-37428
Type: osv

## Details
PowerDNS Recursor up to and including 4.5.9, 4.6.2 and 4.7.1, when protobuf logging is enabled, has Improper Cleanup upon a Thrown Exception, leading to a denial of service (daemon crash) via a DNS query that leads to an answer with specific properties.

## References
- https://docs.powerdns.com/recursor/lua-config/protobuf.html
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2022-02.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37428.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FXSREJKTT6RNE3GXQENQ4R4HS37UNSPX/
- https://nvd.nist.gov/vuln/detail/CVE-2022-37428
