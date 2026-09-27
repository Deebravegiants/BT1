# [M] Insufficient input filtering of "package name" allows command execution in the device with shell privileges

## Summary
Severity: Medium
Advisory: CVE-2024-32653
Aliases: GHSA-3pp3-hg2q-9gpm
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:H)
Published: 2024-04-22
Source: https://osv.dev/vulnerability/CVE-2024-32653
Type: osv

## Details
jadx is a  Dex to Java decompiler. Prior to version 1.5.0,  the package name is not filtered before concatenation. This can be exploited to inject arbitrary code into the package name. The vulnerability allows an attacker to execute commands with shell privileges. Version 1.5.0 contains a patch for the vulnerability.

## References
- https://github.com/skylot/jadx/blob/9114821fb12558874e01421bf38b0d34fb39df72/jadx-gui/src/main/java/jadx/gui/device/protocol/ADBDevice.java#L108-L109
- https://github.com/skylot/jadx/releases/tag/v1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/32xxx/CVE-2024-32653.json
- https://github.com/skylot/jadx/security/advisories/GHSA-3pp3-hg2q-9gpm
- https://nvd.nist.gov/vuln/detail/CVE-2024-32653
