# [H] RGW DoS attack with empty HTTP header in S3 object copy

## Summary
Severity: High
Advisory: BIT-ceph-2024-47866
Aliases: CVE-2024-47866, GHSA-mgrm-g92q-f8h8
Ecosystem: Bitnami
Published: 2026-03-20
Source: https://osv.dev/vulnerability/BIT-ceph-2024-47866
Type: osv

## Affected
- Bitnami: `ceph` — affected >=0 <20.2.1

## Details
Ceph is a distributed object, block, and file storage platform. In versions up to and including 19.2.3, using the argument `x-amz-copy-source` to put an object and specifying an empty string as its content leads to the RGW daemon crashing, resulting in a DoS attack. As of time of publication, no known patched versions exist.

## References
- http://www.openwall.com/lists/oss-security/2025/11/11/3
- https://github.com/ceph/ceph/security/advisories/GHSA-mgrm-g92q-f8h8
- https://nvd.nist.gov/vuln/detail/CVE-2024-47866
