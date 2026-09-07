# [H] RustFS: Missing Post Policy Validation leads to Arbitrary Object Write

## Summary
Severity: High
Advisory: GHSA-w5fh-f8xh-5x3p
CVE: CVE-2026-27607
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-w5fh-f8xh-5x3p
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=1.0.0-alpha.56 <1.0.0-alpha.83

## Details
### Summary
RustFS does not validate policy conditions in presigned POST uploads (PostObject), allowing attackers to bypass content-length-range, starts-with, and Content-Type constraints. This enables unauthorized file uploads exceeding size limits, uploads to arbitrary object keys, and content-type spoofing, potentially leading to storage exhaustion, unauthorized data access, and security bypasses.

### Details
When generating presigned POST URLs via the AWS SDK, applications can specify policy conditions to restrict uploads. RustFS accepts these presigned requests but fails to validate the following conditions server-side:

1. `content-length-range` not enforced: The server does not verify that the uploaded file size falls within the specified minimum and maximum bounds. An attacker can upload arbitrarily large files despite restrictions.
2. `starts-with` not enforced: The server does not validate that the object key matches the required prefix. An attacker can modify the key field to upload files to any path in the bucket.
3. `Content-Type` (exact match) not enforced: The server does not verify that the uploaded file's content type matches the policy constraint. An attacker can upload files with any content type.

The vulnerability exists in the PostObject endpoint implementation, where the signed policy conditions are not parsed and validated against the actual upload request.

### Impact
Vulnerability Type: Improper Input Validation / Authorization Bypass
##### Who is affected:
Any application using RustFS as an S3-compatible backend that relies on presigned POST policy conditions for access control or upload restrictions.
##### Potential attack scenarios:
1. Storage Exhaustion / Denial of Service: Attackers can upload arbitrarily large files, bypassing size limits, potentially filling up disk space and causing service outages.
2. Unauthorized Data Access/Modification: By bypassing starts-with conditions, attackers can upload files to restricted paths (e.g., overwriting configuration files, accessing other users' directories in multi-tenant systems).
3. Content-Type Spoofing: Bypassing content-type restrictions could enable serving malicious content (e.g., HTML/JavaScript files in contexts expecting only images), potentially leading to XSS attacks if files are served to browsers.

**Severity**:  The vulnerability allows complete bypass of server-enforced upload policies, undermining the security model that applications rely upon.

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-w5fh-f8xh-5x3p
- https://nvd.nist.gov/vuln/detail/CVE-2026-27607
- https://github.com/rustfs/rustfs
- https://github.com/rustfs/rustfs/releases/tag/1.0.0-alpha.83
