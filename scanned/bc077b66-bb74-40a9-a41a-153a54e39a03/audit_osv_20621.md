# [H] CVE-2021-3560

## Summary
Severity: High
Advisory: CVE-2021-3560
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-3560
Type: osv

## Details
It was found that polkit could be tricked into bypassing the credential checks for D-Bus requests, elevating the privileges of the requestor to the root user. This flaw could be used by an unprivileged local attacker to, for example, create a new local administrator. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2021-3560
- http://packetstormsecurity.com/files/172836/polkit-Authentication-Bypass.html
- http://packetstormsecurity.com/files/172846/Facebook-Fizz-Denial-Of-Service.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1961710
- https://github.blog/2021-06-10-privilege-escalation-polkit-root-on-linux-with-bug/
