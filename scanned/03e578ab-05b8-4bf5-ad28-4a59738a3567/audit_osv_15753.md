# [H] CVE-2019-19350

## Summary
Severity: High
Advisory: CVE-2019-19350
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-24
Source: https://osv.dev/vulnerability/CVE-2019-19350
Type: osv

## Details
An insecure modification vulnerability in the /etc/passwd file was found in the openshift/ansible-service-broker as shipped in Red Hat Openshift 4 and 3.11. An attacker with access to the container could use this flaw to modify /etc/passwd and escalate their privileges.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1791534
- https://bugzilla.redhat.com/show_bug.cgi?id=1793283
