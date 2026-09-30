# [H] CVE-2015-9016

## Summary
Severity: High
Advisory: CVE-2015-9016
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-05
Source: https://osv.dev/vulnerability/CVE-2015-9016
Type: osv

## Details
In blk_mq_tag_to_rq in blk-mq.c in the upstream kernel, there is a possible use after free due to a race condition when a request has been previously freed by blk_mq_complete_request. This could lead to local escalation of privilege. Product: Android. Versions: Android kernel. Android ID: A-63083046.

## References
- https://github.com/torvalds/linux/commit/0048b4837affd153897ed1222283492070027aa9
- https://source.android.com/security/bulletin/2018-02-01
- https://www.debian.org/security/2018/dsa-4187
- https://github.com/torvalds/linux/commit/0048b4837affd153897ed1222283492070027aa9
- https://source.android.com/security/bulletin/2018-02-01
