# [M] The Bastion ttyrec files are not signed after encryption by the osh-encrypt-rsync script

## Summary
Severity: Medium
Advisory: CVE-2025-59339
Aliases: GHSA-h66q-g57p-rgg6
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2025-59339
Type: osv

## Details
The Bastion provides authentication, authorization, traceability and auditability for SSH accesses. Session-recording ttyrec files, may be handled by the provided osh-encrypt-rsync script that is a helper to rotate, encrypt, sign, copy, and optionally move them to a remote storage periodically, if configured to. When running, the script properly rotates and encrypts the files using the provided GPG key(s), but silently fails to sign them, even if asked to.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59339.json
- https://github.com/ovh/the-bastion/security/advisories/GHSA-h66q-g57p-rgg6
- https://nvd.nist.gov/vuln/detail/CVE-2025-59339
- https://github.com/ovh/the-bastion/commit/9bc85ec3f4b724f903773ba64909777c4826a13f
