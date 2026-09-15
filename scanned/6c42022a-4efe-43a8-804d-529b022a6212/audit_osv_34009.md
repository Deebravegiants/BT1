# [M] Meshtastic firmware allows forged DMs with no PKC to show up as encrypted

## Summary
Severity: Medium
Advisory: CVE-2025-53627
Aliases: GHSA-377p-prwp-4hwf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/CVE-2025-53627
Type: osv

## Details
Meshtastic is an open source mesh networking solution. The Meshtastic firmware (starting from version 2.5) introduces asymmetric encryption (PKI) for direct messages, but when the `pki_encrypted` flag is missing, the firmware silently falls back to legacy AES-256-CTR channel encryption. This was an intentional decision to maintain backwards compatibility. However, the end-user applications, like Web app, iOS/Android app, and applications built on top of Meshtastic using the SDK, did not have a way to differentiate between end-to-end encrypted DMs and the legacy DMs. This creates a downgrade attack path where adversaries who know a shared channel key can craft and inject spoofed direct messages that are displayed as if they were PKC encrypted. Users are not given any feedback of whether a direct message was decrypted with PKI or with legacy symmetric encryption, undermining the expected security guarantees of the PKI rollout. Version 2.7.15 fixes this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53627.json
- https://github.com/meshtastic/firmware/security/advisories/GHSA-377p-prwp-4hwf
- https://nvd.nist.gov/vuln/detail/CVE-2025-53627
