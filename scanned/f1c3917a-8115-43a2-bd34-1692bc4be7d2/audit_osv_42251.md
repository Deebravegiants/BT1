# [M] Deskflow: Clipboard receiver can accumulate data beyond Deskflow's configured clipboard size limit

## Summary
Severity: Medium
Advisory: CVE-2026-65976
Aliases: GHSA-jf7g-qghg-p54x
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-65976
Type: osv

## Details
Deskflow is a keyboard and mouse sharing app. From 1.17.0 until continuous build 1.26.0.300, a connected peer can send repeated DCLP DataChunk messages to ClipboardChunk::assemble() in src/lib/deskflow/ClipboardChunk.cpp, causing the server path in src/lib/server/ClientProxy1_6.cpp or client path in src/lib/client/ServerProxy.cpp to append data beyond the DataStart declared size and configured clipboard limit before DataEnd validation, exhausting receiver memory. This issue is fixed in continuous build 1.26.0.300.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65976.json
- https://github.com/deskflow/deskflow/security/advisories/GHSA-jf7g-qghg-p54x
- https://nvd.nist.gov/vuln/detail/CVE-2026-65976
- https://github.com/deskflow/deskflow/commit/8a535fd5dd48315eaaf6b93d5c7534d0592addef
- https://github.com/deskflow/deskflow/commit/bcd3a658fc3b2ad735146fdc9efefa9462d195b7
