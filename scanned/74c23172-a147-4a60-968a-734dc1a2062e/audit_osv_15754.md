# [H] CVE-2019-19351

## Summary
Severity: High
Advisory: CVE-2019-19351
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-18
Source: https://osv.dev/vulnerability/CVE-2019-19351
Type: osv

## Details
An insecure modification vulnerability in the /etc/passwd file was found in the container openshift/jenkins. An attacker with access to the container could use this flaw to modify /etc/passwd and escalate their privileges. This CVE is specific to the openshift/jenkins-slave-base-rhel7-containera as shipped in Openshift 4 and 3.11.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-19351
