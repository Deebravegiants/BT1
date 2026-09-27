# [H] CVE-2020-0444

## Summary
Severity: High
Advisory: CVE-2020-0444
Aliases: A-150693166, ASB-A-150693166
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-14
Source: https://osv.dev/vulnerability/CVE-2020-0444
Type: osv

## Details
In audit_free_lsm_field of auditfilter.c, there is a possible bad kfree due to a logic error in audit_data_to_entry. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-150693166References: Upstream kernel

## References
- https://source.android.com/security/bulletin/2020-12-01
- https://source.android.com/security/bulletin/2020-12-01
