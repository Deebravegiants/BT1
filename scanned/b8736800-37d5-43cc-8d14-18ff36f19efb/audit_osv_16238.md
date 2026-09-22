# [C] CVE-2019-3807

## Summary
Severity: Critical
Advisory: CVE-2019-3807
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-29
Source: https://osv.dev/vulnerability/CVE-2019-3807
Type: osv

## Details
An issue has been found in PowerDNS Recursor versions 4.1.x before 4.1.9 where records in the answer section of responses received from authoritative servers with the AA flag not set were not properly validated, allowing an attacker to bypass DNSSEC validation.

## References
- https://docs.powerdns.com/recursor/security-advisories/powerdns-advisory-2019-02.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3807
