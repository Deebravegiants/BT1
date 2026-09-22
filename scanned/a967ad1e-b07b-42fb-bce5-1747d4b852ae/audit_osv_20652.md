# [M] CVE-2021-3569

## Summary
Severity: Medium
Advisory: CVE-2021-3569
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-06-03
Source: https://osv.dev/vulnerability/CVE-2021-3569
Type: osv

## Details
A stack corruption bug was found in libtpms in versions before 0.7.2 and before 0.8.0 while decrypting data using RSA. This flaw could result in a SIGBUS (bad memory access) and termination of swtpm. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1964358
