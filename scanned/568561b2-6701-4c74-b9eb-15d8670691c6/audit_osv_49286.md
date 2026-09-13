# [H] CVE-2018-9234

## Summary
Severity: High
Advisory: CVE-2018-9234
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9234
Type: osv

## Details
GnuPG 2.2.4 and 2.2.5 does not enforce a configuration in which key certification requires an offline master Certify key, which results in apparently valid certifications that occurred only with access to a signing subkey.

## References
- https://usn.ubuntu.com/3675-1/
- https://dev.gnupg.org/T3844
