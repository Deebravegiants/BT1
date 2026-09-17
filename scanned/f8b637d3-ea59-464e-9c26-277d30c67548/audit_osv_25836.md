# [H] Prototype pollution vulnerability leading to arbitrary code execution in synchrony deobfuscator

## Summary
Severity: High
Advisory: CVE-2023-45811
Aliases: GHSA-jg82-xh3w-rhxx
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-10-17
Source: https://osv.dev/vulnerability/CVE-2023-45811
Type: osv

## Details
Synchrony deobfuscator is a javascript cleaner & deobfuscator.  A `__proto__` pollution vulnerability exists in versions before v2.4.4. Successful exploitation could lead to arbitrary code execution. A `__proto__` pollution vulnerability exists in the `LiteralMap` transformer allowing crafted input to modify properties in the Object prototype. A fix has been released in `deobfuscator@2.4.4`. Users are advised to upgrade. Users unable to upgrade should launch node with the [--disable-proto=delete][disable-proto] or [--disable-proto=throw][disable-proto] flags

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45811.json
- https://github.com/relative/synchrony/security/advisories/GHSA-jg82-xh3w-rhxx
- https://github.com/relative/synchrony/security/advisories/src/transformers/literalmap.ts
- https://nvd.nist.gov/vuln/detail/CVE-2023-45811
- https://github.com/relative/synchrony/commit/b583126be94c4db7c5a478f1c5204bfb4162cf40
