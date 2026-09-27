# [M] NortheBridge/luminalshine has Incorrect Permission Assignment for Critical Resource and Creation of Temporary File in Directory with Insecure Permissions

## Summary
Severity: Medium
Advisory: CVE-2026-50544
Aliases: GHSA-52q6-5x97-2747
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-50544
Type: osv

## Details
NortheBridge/luminalshine is a Sunshine-compatible game stream host for Moonlight. Prior to version 26.05.0-rc4, a latent gap exists on a default install, the file at `src/platform/windows/misc.cpp` lives at `C:\ProgramData\LuminalShine\config\apps.json` and is created by the `SYSTEM` service. Under Windows' default `C:\ProgramData` inheritance, that gives `BUILTIN\Users` only Read+Execute — not writable — so the canonical EoP doesn't actually trigger on a vanilla install. Version 26.05.0-rc4 contains a patch for the issue. As a workaround, use default condition DACLs for `ProgramData`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50544.json
- https://github.com/NortheBridge/luminalshine/security/advisories/GHSA-52q6-5x97-2747
- https://nvd.nist.gov/vuln/detail/CVE-2026-50544
