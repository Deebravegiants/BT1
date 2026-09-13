# [M] CVE-2018-1079

## Summary
Severity: Medium
Advisory: CVE-2018-1079
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-04-12
Source: https://osv.dev/vulnerability/CVE-2018-1079
Type: osv

## Details
pcs before version 0.9.164 and 0.10 is vulnerable to a privilege escalation via authorized user malicious REST call. The REST interface of the pcsd service did not properly sanitize the file name from the /remote/put_file query. If the /etc/booth directory exists, an authenticated attacker with write permissions could create or overwrite arbitrary files with arbitrary data outside of the /etc/booth directory, in the context of the pcsd process.

## References
- https://access.redhat.com/errata/RHSA-2018:1060
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1079
