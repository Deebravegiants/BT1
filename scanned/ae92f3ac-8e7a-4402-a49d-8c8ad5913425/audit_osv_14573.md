# [H] CVE-2019-10147

## Summary
Severity: High
Advisory: CVE-2019-10147
CVSS: 7.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H)
Published: 2019-06-03
Source: https://osv.dev/vulnerability/CVE-2019-10147
Type: osv

## Details
rkt through version 1.30.0 does not isolate processes in containers that are run with `rkt enter`. Processes run with `rkt enter` are not limited by cgroups during stage 2 (the actual environment in which the applications run). Compromised containers could exploit this flaw to access host resources.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10147
- https://www.twistlock.com/labs-blog/breaking-out-of-coresos-rkt-3-new-cves/
