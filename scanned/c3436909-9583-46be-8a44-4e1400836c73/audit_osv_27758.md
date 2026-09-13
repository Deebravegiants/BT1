# [H] Crafted responses can lead to a denial of service in Recursor if recursive forwarding is configured

## Summary
Severity: High
Advisory: CVE-2024-25583
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-25
Source: https://osv.dev/vulnerability/CVE-2024-25583
Type: osv

## Details
A crafted response from an upstream server the recursor has been configured to forward-recurse to can cause a Denial of Service in the Recursor. The default configuration of the Recursor does not use recursive forwarding and is not affected.

## References
- http://www.openwall.com/lists/oss-security/2024/04/24/1
- https://repo.powerdns.com/
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2024-02.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25583.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-25583
- https://github.com/PowerDNS/pdns
