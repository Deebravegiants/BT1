# [H] CVE-2017-17840

## Summary
Severity: High
Advisory: CVE-2017-17840
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-27
Source: https://osv.dev/vulnerability/CVE-2017-17840
Type: osv

## Details
An issue was discovered in Open-iSCSI through 2.0.875. A local attacker can cause the iscsiuio server to abort or potentially execute code by sending messages with incorrect lengths, which (due to lack of checking) can lead to buffer overflows, and result in aborts (with overflow checking enabled) or code execution. The process_iscsid_broadcast function in iscsiuio/src/unix/iscsid_ipc.c does not validate the payload length before a write operation.

## References
- http://www.openwall.com/lists/oss-security/2017/12/13/2
- https://bugzilla.opensuse.org/show_bug.cgi?id=1072312
