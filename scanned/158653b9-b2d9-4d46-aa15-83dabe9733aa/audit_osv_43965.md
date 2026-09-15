# [M] adm-zip 0.5.9 through 0.6.0 Arbitrary File Overwrite via Symlink Following on Extraction

## Summary
Severity: Medium
Advisory: CVE-2026-76845
Aliases: GHSA-vwc7-r8mq-g2x9
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-24
Source: https://osv.dev/vulnerability/CVE-2026-76845
Type: osv

## Details
adm-zip 0.5.9 through 0.6.0 follows symbolic links at the extraction destination. Utils.sanitize in util/utils.js enforces containment by comparing only the string form of an archive entry name against the resolved extraction root, and Utils.writeFileTo opens the computed destination with fs.openSync(path, "w", 0o666), which resolves symbolic links and carries neither O_NOFOLLOW nor a pre-write fs.lstatSync check. When a path component at the destination already exists as a symbolic link pointing outside the extraction root, extractAllTo, extractAllToAsync and extractEntryTo write the entry contents through that link and then chmod its target, placing attacker-controlled content in a file outside the root without any traversal sequence appearing in the archive. Reaching the write requires overwrite to be enabled, because the preceding fs.existsSync check also resolves the link and otherwise declines. An attacker able to create a symbolic link inside a shared, reused or predictable extraction directory, such as a temporary directory or a continuous integration workspace, can overwrite any file the extracting process is permitted to write.

## References
- https://www.npmjs.com/package/adm-zip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76845.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76845
- https://www.vulncheck.com/advisories/adm-zip-through-arbitrary-file-overwrite-via-symlink-following-on-extraction
- https://github.com/cthackers/adm-zip
- https://github.com/cthackers/adm-zip/blob/v0.6.0/util/utils.js
