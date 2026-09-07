# [M] EVE: SSH as Root Unlockable Without Triggering Measured Boot

## Summary
Severity: Medium
Advisory: GHSA-3mq9-xhgq-r7gj
CVE: CVE-2023-43631
CWE: CWE-522, CWE-922
Ecosystem: Go
CVSS: CVSS:3.1/AV:P/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-3mq9-xhgq-r7gj
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve` — affected >=0 <0.0.0-20220708121648-5fef4d92e758

## Details
### Impact

On boot, the Pillar container checks for /config/authorized_keys. If present with a valid public key, it enables SSH on port 22 with root login. The /config partition is not protected by measured boot, is mutable and unencrypted.

This enables an attacker with physical access to the device to take out the disk, modify the /config partition using a separate server, then insert it, without the inserted key being flagged as an integrity voilation my measured boot and remote attestation.

### Patches

Patched in 9.4.3-lts

### Workarounds

None (apart from preventing physical access to the device)

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-3mq9-xhgq-r7gj
- https://nvd.nist.gov/vuln/detail/CVE-2023-43631
- https://github.com/lf-edge/eve/commit/5fef4d92e75838cc78010edaed5247dfbdae1889
- https://github.com/lf-edge/eve/commit/aa3501d6c57206ced222c33aea15a9169d629141
- https://asrg.io/security-advisories/cve-2023-43631
- https://asrg.io/security-advisories/ssh-as-root-unlockable-without-triggering-measured-boot
- https://github.com/lf-edge/eve
