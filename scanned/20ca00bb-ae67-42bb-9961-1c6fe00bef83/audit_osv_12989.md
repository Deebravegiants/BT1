# [H] CVE-2018-16790

## Summary
Severity: High
Advisory: CVE-2018-16790
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2018-16790
Type: osv

## Details
_bson_iter_next_internal in bson-iter.c in libbson 1.12.0, as used in MongoDB mongo-c-driver and other products, has a heap-based buffer over-read via a crafted bson buffer.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00012.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1627923#c3
- https://jira.mongodb.org/browse/CDRIVER-2819
- https://github.com/mongodb/mongo-c-driver/commit/0d9a4d98bfdf4acd2c0138d4aaeb4e2e0934bd84
