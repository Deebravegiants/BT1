# [H] CVE-2017-7572

## Summary
Severity: High
Advisory: CVE-2017-7572
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-06
Source: https://osv.dev/vulnerability/CVE-2017-7572
Type: osv

## Details
The _checkPolkitPrivilege function in serviceHelper.py in Back In Time (aka backintime) 1.1.18 and earlier uses a deprecated polkit authorization method (unix-process) that is subject to a race condition (time of check, time of use). With this authorization method, the owner of a process requesting a polkit operation is checked by polkitd via /proc/<pid>/status, by which time the requesting process may have been replaced by a different process with the same PID that has different privileges then the original requester.

## References
- https://github.com/bit-team/backintime/commit/7f208dc547f569b689c888103e3b593a48cd1869
