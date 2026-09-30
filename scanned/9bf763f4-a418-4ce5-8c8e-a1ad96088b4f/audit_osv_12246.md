# [H] CVE-2018-1102

## Summary
Severity: High
Advisory: CVE-2018-1102
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-30
Source: https://osv.dev/vulnerability/CVE-2018-1102
Type: osv

## Details
A flaw was found in source-to-image function as shipped with Openshift Enterprise 3.x. An improper path validation of tar files in ExtractTarStreamFromTarReader in tar/tar.go leads to privilege escalation.

## References
- https://access.redhat.com/errata/RHSA-2018:1227
- https://access.redhat.com/errata/RHSA-2018:1229
- https://access.redhat.com/errata/RHSA-2018:1231
- https://access.redhat.com/errata/RHSA-2018:1233
- https://access.redhat.com/errata/RHSA-2018:1235
- https://access.redhat.com/errata/RHSA-2018:1237
- https://access.redhat.com/errata/RHSA-2018:1239
- https://access.redhat.com/errata/RHSA-2018:1241
- https://access.redhat.com/errata/RHSA-2018:1243
- https://access.redhat.com/errata/RHSA-2019:0036
- https://bugzilla.redhat.com/show_bug.cgi?id=1562246
