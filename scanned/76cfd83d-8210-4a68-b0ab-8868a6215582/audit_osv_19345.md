# [H] CVE-2021-20264

## Summary
Severity: High
Advisory: CVE-2021-20264
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-06
Source: https://osv.dev/vulnerability/CVE-2021-20264
Type: osv

## Details
An insecure modification flaw in the /etc/passwd file was found in the openjdk-1.8 and openjdk-11 containers. This flaw allows an attacker with access to the container to modify the /etc/passwd and escalate their privileges. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1932283
