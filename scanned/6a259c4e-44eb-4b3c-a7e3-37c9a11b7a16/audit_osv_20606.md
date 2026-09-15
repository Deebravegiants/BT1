# [H] CVE-2021-3551

## Summary
Severity: High
Advisory: CVE-2021-3551
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-3551
Type: osv

## Details
A flaw was found in the PKI-server, where the spkispawn command, when run in debug mode, stores admin credentials in the installation log file. This flaw allows a local attacker to retrieve the file to obtain the admin password and gain admin privileges to the Dogtag CA manager. The highest threat from this vulnerability is to confidentiality.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1959971
