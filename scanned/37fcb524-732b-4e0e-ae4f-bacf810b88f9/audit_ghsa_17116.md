# [M] LibOSDP vulnerable to a null pointer deref in osdp_reply_name

## Summary
Severity: Medium
Advisory: GHSA-7945-5mcv-f2pp
CVE: CVE-2024-52296
CWE: CWE-476
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-08
Source: https://github.com/advisories/GHSA-7945-5mcv-f2pp
Type: github-advisory

## Affected
- PyPI: `libosdp` — affected >=0 <2.4.0

## Details
### Issue:
At ospd_common.c, on the osdp_reply_name function, any reply id between REPLY_ACK and REPLY_XRD is valid, but names array do not declare all of the range. On a case of an undefined reply id within the range, name will be null (`name = names[reply_id - REPLY_ACK];`). Null name will casue a crash on next line: `if (name[0] == '\0')` as null[0] is invalid.

### Attack:
As this logic is not limited to a secure connection, attacker may trigger this vulnerability without any prior knowledge.

### Impact
Denial of Service

### Patch
The issue has been patched in 24409e98a260176765956ec766a04cb35984fab1

## References
- https://github.com/goToMain/libosdp/security/advisories/GHSA-7945-5mcv-f2pp
- https://nvd.nist.gov/vuln/detail/CVE-2024-52296
- https://github.com/goToMain/libosdp/commit/24409e98a260176765956ec766a04cb35984fab1
- https://github.com/goToMain/libosdp
