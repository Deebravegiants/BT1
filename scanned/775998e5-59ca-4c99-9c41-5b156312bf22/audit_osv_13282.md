# [H] CVE-2018-19093

## Summary
Severity: High
Advisory: CVE-2018-19093
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-19093
Type: osv

## Details
An issue has been found in libIEC61850 v1.3. It is a SEGV in ControlObjectClient_setCommandTerminationHandler in client/client_control.c. NOTE: the software maintainer disputes this because it requires incorrect usage of the client_example_control program

## References
- https://github.com/fouzhe/security/tree/master/libiec61850#segv-in-function-controlobjectclient_setcommandterminationhandler
- https://github.com/mz-automation/libiec61850/issues/84
