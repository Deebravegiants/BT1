# [H] CVE-2022-40617

## Summary
Severity: High
Advisory: CVE-2022-40617
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-31
Source: https://osv.dev/vulnerability/CVE-2022-40617
Type: osv

## Details
strongSwan before 5.9.8 allows remote attackers to cause a denial of service in the revocation plugin by sending a crafted end-entity (and intermediate CA) certificate that contains a CRL/OCSP URL that points to a server (under the attacker's control) that doesn't properly respond but (for example) just does nothing after the initial TCP handshake, or sends an excessive amount of application data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40617.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J3GAYIOCSLU57C45CO4UE4IV4JZE4W3L/
- https://nvd.nist.gov/vuln/detail/CVE-2022-40617
- https://www.strongswan.org/blog/2022/10/03/strongswan-vulnerability-%28cve-2022-40617%29.html
