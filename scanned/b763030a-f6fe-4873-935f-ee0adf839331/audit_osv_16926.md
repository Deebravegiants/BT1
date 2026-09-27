# [H] CVE-2020-10728

## Summary
Severity: High
Advisory: CVE-2020-10728
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-16
Source: https://osv.dev/vulnerability/CVE-2020-10728
Type: osv

## Details
A flaw was found in automationbroker/apb container in versions up to and including 2.0.4-1. This container grants all users sudoer permissions allowing an unauthorized user with access to the running container the ability to escalate their own privileges. The highest threat from this vulnerability is to data confidentiality and integrity as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1829674
