# [M] Unclaimed S3 Bucket Reference in psf/requests Documentation

## Summary
Severity: Medium
Advisory: CVE-2024-1682
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-1682
Type: osv

## Details
An unclaimed Amazon S3 bucket, 'codeconf', is referenced in an audio file link within the .rst documentation file. This bucket has been claimed by an external party. The use of this unclaimed S3 bucket could lead to data integrity issues, data leakage, availability problems, loss of trustworthiness, and potential further attacks if the bucket is used to host malicious content or as a pivot point for further attacks.

## References
- https://huntr.com/bounties/4da5ded5-b59b-4ece-8812-46a4329e446c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/1xxx/CVE-2024-1682.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-1682
- https://github.com/psf/requests/commit/6106a63eb6c0fa490efa73d44388ac25b1b08af4
