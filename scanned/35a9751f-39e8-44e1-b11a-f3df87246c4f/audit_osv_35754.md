# [M] Develar's electron-builder allows arbitrary file overwrite

## Summary
Severity: Medium
Advisory: CVE-2026-13723
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-13723
Type: osv

## Details
A vulnerability in the `zipx.Unzip` extraction routine of Develar's app-builder allows an attacker to overwrite arbitrary files on macOS APFS by exploiting a Unicode Normalization Collision combined with symlink following behavior. APFS treats certain Unicode equivalent filenames as identical (e.g., ß ↔ ss), while app builder performs no canonical normalization before validating or writing paths. As a result, a crafted ZIP archive containing:
•	a symlink entry named ss pointing to a target file, and
•	a regular file named ß containing attacker controlled data,
will cause the second write to follow the symlink and overwrite the target file.

## References
- http://kb.cert.org/vuls/id/293714
- https://www.kb.cert.org/vuls/id/293714
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13723.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13723
- https://github.com/develar/app-builder/pull/163
- https://github.com/develar/app-builder
