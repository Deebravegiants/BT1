# [H] Rufus has Local Privilege Escalation via TOCTOU Race Condition in Fido Script Handling

## Summary
Severity: High
Advisory: CVE-2026-23988
Aliases: GHSA-hcx5-hrhj-xhq9
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-23988
Type: osv

## Details
Rufus is a utility that helps format and create bootable USB flash drives. Versions 4.11 and below contain a race condition (TOCTOU) in src/net.c during the creation, validation, and execution of the Fido PowerShell script. Since Rufus runs with elevated privileges (Administrator) but writes the script to the %TEMP% directory (writeable by standard users) without locking the file, a local attacker can replace the legitimate script with a malicious one between the file write operation and the execution step. This allows arbitrary code execution with Administrator privileges. This issue has been fixed in version 4.12_BETA.

## References
- https://github.com/pbatard/rufus/releases/tag/v4.12_BETA
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23988.json
- https://github.com/pbatard/rufus/security/advisories/GHSA-hcx5-hrhj-xhq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-23988
- https://github.com/pbatard/rufus/commit/460cc5768aa45be07941b9e4ebc9bee02d282873
