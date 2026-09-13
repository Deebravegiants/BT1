# [H] CVE-2020-12667

## Summary
Severity: High
Advisory: CVE-2020-12667
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-12667
Type: osv

## Details
Knot Resolver before 5.1.1 allows traffic amplification via a crafted DNS answer from an attacker-controlled server, aka an "NXNSAttack" issue. This is triggered by random subdomains in the NSDNAME in NS records.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/76Y4FITMOH6RVPWAANGV7NB2ZHPJJGDQ/
- http://cyber-security-group.cs.tau.ac.il/#
- http://www.openwall.com/lists/oss-security/2020/05/19/2
- https://en.blog.nic.cz/2020/05/19/nxnsattack-upgrade-resolvers-to-stop-new-kind-of-random-subdomain-attack/
- https://www.knot-resolver.cz/2020-05-19-knot-resolver-5.1.1.html
