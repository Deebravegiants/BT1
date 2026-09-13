# [M] EVerest has Delayed Authorization Response Bypasses Termination After RemoteStop

## Summary
Severity: Medium
Advisory: CVE-2026-33014
Aliases: GHSA-43xm-5m3v-52hm
CVSS: 5.2 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33014
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2026.02.0, during RemoteStop processing, a delayed authorization response restores `authorized` back to true, defeating the `stop_transaction()` call condition on PowerOff events. As a result, the transaction can remain open even after a remote stop. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33014.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-43xm-5m3v-52hm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33014
