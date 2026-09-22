# [C] CVE-2024-56431

## Summary
Severity: Critical
Advisory: CVE-2024-56431
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-25
Source: https://osv.dev/vulnerability/CVE-2024-56431
Type: osv

## Details
oc_huff_tree_unpack in huffdec.c in libtheora in Theora through 1.0 7180717 has an invalid negative left shift. NOTE: this is disputed by third parties because there is no evidence of a security impact, e.g., an application would not crash.

## References
- http://www.openwall.com/lists/oss-security/2025/04/25/4
- http://www.openwall.com/lists/oss-security/2025/04/25/6
- https://github.com/xiph/theora/blob/7180717276af1ebc7da15c83162d6c5d6203aabf/lib/huffdec.c#L193
- https://www.openwall.com/lists/oss-security/2025/04/25/6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56431.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56431
- https://github.com/xiph/theora/issues/17#issuecomment-2480630603
- https://github.com/UnionTech-Software/libtheora-CVE-2024-56431-PoC
