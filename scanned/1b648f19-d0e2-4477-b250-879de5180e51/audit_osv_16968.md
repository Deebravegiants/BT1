# [H] CVE-2020-10995

## Summary
Severity: High
Advisory: CVE-2020-10995
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-10995
Type: osv

## Details
PowerDNS Recursor from 4.1.0 up to and including 4.3.0 does not sufficiently defend against amplification attacks. An issue in the DNS protocol has been found that allow malicious parties to use recursive DNS services to attack third party authoritative name servers. The attack uses a crafted reply by an authoritative name server to amplify the resulting traffic between the recursive and other authoritative name servers. Both types of service can suffer degraded performance as an effect. This is triggered by random subdomains in the NSDNAME in NS records. PowerDNS Recursor 4.1.16, 4.2.2 and 4.3.1 contain a mitigation to limit the impact of this DNS protocol issue.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NMP72NJGKBWR5WEBXAWX5KSLQUDFTG6S/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PS4ZN5XGENYNFKX7QIIOUCQQHXE37GJF/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00052.html
- http://www.nxnsattack.com
- https://doc.powerdns.com/recursor/security-advisories/powerdns-advisory-2020-01.html
- https://www.debian.org/security/2020/dsa-4691
