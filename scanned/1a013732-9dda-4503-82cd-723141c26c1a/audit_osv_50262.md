# [H] CVE-2020-0433

## Summary
Severity: High
Advisory: CVE-2020-0433
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-17
Source: https://osv.dev/vulnerability/CVE-2020-0433
Type: osv

## Details
In blk_mq_queue_tag_busy_iter of blk-mq-tag.c, there is a possible use after free due to improper locking. This could lead to local escalation of privilege with no additional execution privileges needed. User interaction is not needed for exploitation.Product: AndroidVersions: Android kernelAndroid ID: A-151939299

## References
- https://source.android.com/security/bulletin/pixel/2020-09-01
- https://source.android.com/security/bulletin/pixel/2020-09-01
