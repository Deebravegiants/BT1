# [H] End-to-end encryption device setup did not verify public key

## Summary
Severity: High
Advisory: BIT-nextcloud-2021-32727
Aliases: CVE-2021-32727, GHSA-5v33-r9cm-7736
Ecosystem: Bitnami
Published: 2026-07-12
Source: https://osv.dev/vulnerability/BIT-nextcloud-2021-32727
Type: osv

## Affected
- Bitnami: `nextcloud` — affected >=0 <3.16.1

## Details
Nextcloud Android Client is the Android client for Nextcloud. Clients using the Nextcloud end-to-end encryption feature download the public and private key via an API endpoint. In versions prior to 3.16.1, the Nextcloud Android client skipped a step that involved the client checking if a private key belonged to a previously downloaded public certificate. If the Nextcloud instance served a malicious public key, the data would be encrypted for this key and thus could be accessible to a malicious actor. The vulnerability is patched in version 3.16.1. As a workaround, do not add additional end-to-end encrypted devices to a user account.

## References
- https://github.com/nextcloud/android/pull/8438
- https://github.com/nextcloud/end_to_end_encryption_rfc/blob/7f002996397faefb664019a97ebb0a1e210f64f0/RFC.md#further-devices
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-5v33-r9cm-7736
- https://hackerone.com/reports/1189162
- https://nvd.nist.gov/vuln/detail/CVE-2021-32727
