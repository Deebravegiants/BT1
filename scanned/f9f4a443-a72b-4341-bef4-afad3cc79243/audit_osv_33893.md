# [H] Meshtastic Repeated Public and Private Keypairs

## Summary
Severity: High
Advisory: CVE-2025-52464
Aliases: GHSA-gq7v-jr8c-mfr7
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:L/SC:L/SI:L/SA:H)
Published: 2025-06-19
Source: https://osv.dev/vulnerability/CVE-2025-52464
Type: osv

## Details
Meshtastic is an open source mesh networking solution. In versions from 2.5.0 to before 2.6.11, the flashing procedure of several hardware vendors was resulting in duplicated public/private keys. Additionally, the Meshtastic was failing to properly initialize the internal randomness pool on some platforms, leading to possible low-entropy key generation. When users with an affected key pair sent Direct Messages, those message could be captured and decrypted by an attacker that has compiled the list of compromised keys. This issue has been patched in version 2.6.11 where key generation is delayed til the first time the LoRa region is set, along with warning users when a compromised key is detected. Version 2.6.12 furthers this patch by automatically wiping known compromised keys when found. A workaround to this vulnerability involves users doing a complete device wipe to remove vendor-cloned keys.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52464.json
- https://github.com/meshtastic/firmware/security/advisories/GHSA-gq7v-jr8c-mfr7
- https://nvd.nist.gov/vuln/detail/CVE-2025-52464
- https://github.com/meshtastic/firmware/commit/4bf2dd04aeeccc4ba20c79bcaad7a572aabdecad
- https://github.com/meshtastic/firmware/commit/55b2bbf93756fc7bbbfdbc7cbf29f88e6b637f22
- https://github.com/meshtastic/firmware/commit/e5f6804421ac4b76dd31980250a505dba24c2aa6
- https://github.com/meshtastic/firmware/commit/e623c70bd0c2ab9db9baf04888e19d1428310bb9
