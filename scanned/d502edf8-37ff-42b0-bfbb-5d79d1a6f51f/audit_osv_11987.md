# [H] CVE-2018-1000538

## Summary
Severity: High
Advisory: CVE-2018-1000538
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000538
Type: osv

## Details
Minio Inc. Minio S3 server version prior to RELEASE.2018-05-16T23-35-33Z contains a Allocation of Memory Without Limits or Throttling (similar to CWE-774) vulnerability in write-to-RAM that can result in Denial of Service. This attack appear to be exploitable via Sending V4-(pre)signed requests with large bodies . This vulnerability appears to have been fixed in after commit 9c8b7306f55f2c8c0a5c7cea9a8db9d34be8faa7.

## References
- https://github.com/minio/minio/pull/5957
- https://github.com/minio/minio/commit/9c8b7306f55f2c8c0a5c7cea9a8db9d34be8faa7#diff-e8c3bc9bc83b5516d0cc806cd461d08bL220
