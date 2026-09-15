# [H] @joplin/onenote-converter: Path traversal in OneNote importer allows overwriting arbitrary files

## Summary
Severity: High
Advisory: GHSA-gcmj-c9gg-9vh6
CVE: CVE-2026-22810
CWE: CWE-24
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-gcmj-c9gg-9vh6
Type: github-advisory

## Affected
- npm: `@joplin/onenote-converter` — affected >=0 <3.5.7

## Details
### Summary
A path traversal vulnerability in the OneNote importer allows overwriting arbitrary files on disk.

### Details
The OneNote converter does not sanitize the names of embedded files before writing them to disk. As a result, it's possible for an attacker to create a malicious `.one` file that includes file names containing `../../`, that are then interpreted as part of the target path when extracting attachments from the `.one` file.

One affected location is `embedded_file.rs`, which generates a file name from a string previously parsed from the `.one` file,
https://github.com/laurent22/joplin/blob/af5108d70233b1db9410346958c1587cf7c1b16d/packages/onenote-converter/renderer/src/page/embedded_file.rs#L13-L16

Above, [`determine_filename`](https://github.com/laurent22/joplin/blob/af5108d70233b1db9410346958c1587cf7c1b16d/packages/onenote-converter/renderer/src/page/embedded_file.rs#L56-L64) passes through the provided file name.

[Similar logic](https://github.com/laurent22/joplin/blob/4d7fa5972fe2986eae14cbf3a2801835cbe1384e/packages/onenote-converter/src/page/embedded_file.rs#L14) has been present since 4d7fa5972fe2986eae14cbf3a2801835cbe1384e (Joplin 3.2.2), when the OneNote importer was first introduced.

### PoC

[Screencast from 2025-11-20 13-50-21.webm](https://github.com/user-attachments/assets/a9d6cc64-ec11-4f33-9f92-32efe0eaab23)


1. Import [poc_v2.zip](https://github.com/user-attachments/files/23664109/poc_v2.zip).
2. Open the application's profile directory, then open `log.txt`.
3. Observe that `log.txt` has been overwritten non-log-file content (a WAV file).

Tested on Fedora Linux 43 with Joplin 3.4.12 (prod, linux) and Joplin 3.5.6 (dev, linux).

**Note**: The PoC ZIP file overwrites Joplin's `log.txt`. It is also possible to craft a file that overwrites more sensitive system files (e.g. `.bashrc` on Linux).

### Impact
This is a path traversal vulnerability that impacts **all versions of Joplin (<= v3.5.6) that include a OneNote importer**. Importing a crafted OneNote export file allows an attacker to overwrite arbitrary files, potentially leading to remote code execution.

### Patched in

- **Joplin**: https://github.com/laurent22/joplin/commit/791668455e1aae50501ff57ea4783b3fba9d377c
- **one2html**: https://github.com/msiemens/one2html/commit/948d65cdca5bb35d776b8b235ec05ff15249fd41

## References
- https://github.com/laurent22/joplin/security/advisories/GHSA-gcmj-c9gg-9vh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-22810
- https://github.com/laurent22/joplin/pull/13736
- https://github.com/laurent22/joplin/commit/791668455e1aae50501ff57ea4783b3fba9d377c
- https://github.com/laurent22/joplin
- https://github.com/laurent22/joplin/blob/af5108d70233b1db9410346958c1587cf7c1b16d/packages/onenote-converter/renderer/src/page/embedded_file.rs#L13-L16
- https://github.com/laurent22/joplin/releases/tag/v3.5.7
