# [H] CVE-2021-3847

## Summary
Severity: High
Advisory: CVE-2021-3847
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-04-01
Source: https://osv.dev/vulnerability/CVE-2021-3847
Type: osv

## Details
An unauthorized access to the execution of the setuid file with capabilities flaw in the Linux kernel OverlayFS subsystem was found in the way user copying a capable file from a nosuid mount into another mount. A local user could use this flaw to escalate their privileges on the system.

## References
- https://www.openwall.com/lists/oss-security/2021/10/14/3
- https://bugzilla.redhat.com/show_bug.cgi?id=2009704
