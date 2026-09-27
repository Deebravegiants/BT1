# [H] CVE-2018-12088

## Summary
Severity: High
Advisory: CVE-2018-12088
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-10
Source: https://osv.dev/vulnerability/CVE-2018-12088
Type: osv

## Details
S3QL before 2.27 mishandles checksumming, and consequently allows replay attacks in which an attacker who controls the backend can present old versions of the filesystem metadata database as up-to-date, temporarily inject zero-valued bytes into files, or temporarily hide parts of files. This is related to the checksum_basic_mapping function.

## References
- https://groups.google.com/forum/#%21topic/s3ql/4TzCVIMkA4o
- https://bitbucket.org/nikratio/s3ql/commits/85aba5c2d5c81453a73a50ed638adaeef0521020
- https://bitbucket.org/nikratio/s3ql/issues/272/t3_verifypy-test_retrieve-sometimes-fails
