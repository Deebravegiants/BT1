# [M] Meshtastic-Android vulnerable to forged DMs with no PKC showing up as encrypted

## Summary
Severity: Medium
Advisory: CVE-2025-52883
Aliases: GHSA-h4rg-g6f3-ghh7
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-52883
Type: osv

## Details
Meshtastic-Android is an Android application for the mesh radio software Meshtastic. Prior to version 2.5.21, an attacker is able to send an unencrypted direct message to a victim impersonating any other node of the mesh. This message will be displayed in the same chat that the victim normally communicates with the other node and it will appear as using PKC, while it is not. This means that the victim will be provided with a false sense of security due to the green padlock displayed when using PKC and they'll read the attacker's message as legitimate. Version 2.5.21 contains a patch for the issue. It is suggested to implement a stricter control on whether a message has been received using PKC or using the shared Meshtastic channel key. Moreover, instead of showing no green padlock icon in the chat with no PKC, consider using an explicit indicator like, for example, the yellow half-open padlock displayed when in HAM mode. This remediation, however, applies to the client applications rather than the Meshtastic firmware.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52883.json
- https://github.com/meshtastic/Meshtastic-Android/security/advisories/GHSA-h4rg-g6f3-ghh7
- https://nvd.nist.gov/vuln/detail/CVE-2025-52883
- https://github.com/meshtastic/Meshtastic-Android/pull/1720
