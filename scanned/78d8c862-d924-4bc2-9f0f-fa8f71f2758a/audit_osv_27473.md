# [H] Missing array size check in _Mtxinit() in the Xtensa port

## Summary
Severity: High
Advisory: CVE-2024-2214
Aliases: GHSA-vmp6-qhp9-r66x
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-03-26
Source: https://osv.dev/vulnerability/CVE-2024-2214
Type: osv

## Details
In Eclipse ThreadX before version 6.4.0, the _Mtxinit() function in the 
Xtensa port was missing an array size check causing a memory overwrite. 
The affected file was ports/xtensa/xcc/src/tx_clib_lock.c

## References
- http://seclists.org/fulldisclosure/2024/May/35
- http://www.openwall.com/lists/oss-security/2024/05/28/1
- https://github.com/eclipse-threadx/threadx/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2214.json
- https://github.com/eclipse-threadx/threadx/security/advisories/GHSA-vmp6-qhp9-r66x
- https://nvd.nist.gov/vuln/detail/CVE-2024-2214
