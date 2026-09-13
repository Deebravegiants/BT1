# [M] CVE-2018-19792

## Summary
Severity: Medium
Advisory: CVE-2018-19792
CVSS: 6.7 (CVSS:3.0/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/CVE-2018-19792
Type: osv

## Details
The server in LiteSpeed OpenLiteSpeed before 1.5.0 RC6 allows local users to cause a denial of service (buffer overflow) or possibly have unspecified other impact by creating a symlink through which the openlitespeed program can be invoked with a long command name (involving ../ characters), which is mishandled in the LshttpdMain::getServerRootFromExecutablePath function.

## References
- https://github.com/litespeedtech/openlitespeed/issues/117
