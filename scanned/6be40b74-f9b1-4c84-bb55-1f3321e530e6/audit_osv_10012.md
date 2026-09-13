# [H] CVE-2017-12678

## Summary
Severity: High
Advisory: CVE-2017-12678
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-08
Source: https://osv.dev/vulnerability/CVE-2017-12678
Type: osv

## Details
In TagLib 1.11.1, the rebuildAggregateFrames function in id3v2framefactory.cpp has a pointer to cast vulnerability, which allows remote attackers to cause a denial of service or possibly have unspecified other impact via a crafted audio file.

## References
- https://lists.debian.org/debian-lts-announce/2021/09/msg00020.html
- https://github.com/taglib/taglib/commit/cb9f07d9dcd791b63e622da43f7b232adaec0a9a
- https://github.com/taglib/taglib/issues/829
- https://github.com/taglib/taglib/pull/831
