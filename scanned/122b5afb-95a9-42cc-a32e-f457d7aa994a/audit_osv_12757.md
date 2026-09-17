# [M] CVE-2018-14644

## Summary
Severity: Medium
Advisory: CVE-2018-14644
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-09
Source: https://osv.dev/vulnerability/CVE-2018-14644
Type: osv

## Details
An issue has been found in PowerDNS Recursor from 4.0.0 up to and including 4.1.4. A remote attacker sending a DNS query for a meta-type like OPT can lead to a zone being wrongly cached as failing DNSSEC validation. It only arises if the parent zone is signed, and all the authoritative servers for that parent zone answer with FORMERR to a query for at least one of the meta-types. As a result, subsequent queries from clients requesting DNSSEC validation will be answered with a ServFail.

## References
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2018-07.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14644
