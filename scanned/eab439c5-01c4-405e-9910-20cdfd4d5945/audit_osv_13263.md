# [H] CVE-2018-18937

## Summary
Severity: High
Advisory: CVE-2018-18937
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-05
Source: https://osv.dev/vulnerability/CVE-2018-18937
Type: osv

## Details
An issue has been found in libIEC61850 v1.3. It is a NULL pointer dereference in ClientDataSet_getValues in client/ied_connection.c.

## References
- https://github.com/fouzhe/security/tree/master/libiec61850#segv-in-function-clientdataset_getvalues
- https://github.com/mz-automation/libiec61850/issues/82
