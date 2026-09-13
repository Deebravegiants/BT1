# [H] CVE-2021-29461

## Summary
Severity: High
Advisory: CVE-2021-29461
Aliases: GHSA-3m9v-v33c-g83x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-20
Source: https://osv.dev/vulnerability/CVE-2021-29461
Type: osv

## Details
Discord Recon Server is a bot that allows one to do one's reconnaissance process from one's Discord. A vulnerability in Discord Recon Server prior to 0.0.3 could be exploited to read internal files from the system and write files into the system resulting in remote code execution. This issue has been fixed in version 0.0.3. As a workaround, one may copy the code from `assets/CommandInjection.py` in the Discord Recon Server code repository and overwrite vulnerable code from one's own Discord Recon Server implementation with code that contains the patch.

## References
- https://github.com/DEMON1A/Discord-Recon/security/advisories/GHSA-3m9v-v33c-g83x
