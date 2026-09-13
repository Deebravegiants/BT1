# [C] CVE-2019-13624

## Summary
Severity: Critical
Advisory: CVE-2019-13624
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-07-17
Source: https://osv.dev/vulnerability/CVE-2019-13624
Type: osv

## Details
In ONOS 1.15.0, apps/yang/web/src/main/java/org/onosproject/yang/web/YangWebResource.java mishandles backquote characters within strings that can be used in a shell command.

## References
- https://gerrit.onosproject.org/#/c/20767/
