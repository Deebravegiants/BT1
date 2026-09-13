# [M] CVE-2026-31053

## Summary
Severity: Medium
Advisory: CVE-2026-31053
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-31053
Type: osv

## Details
A double free vulnerability exists in librz/bin/format/le/le.c in the function le_load_fixup_record(). When processing malformed or circular LE fixup chains, relocation entries may be freed multiple times during error handling. A specially crafted LE binary can trigger heap corruption and cause the application to crash, resulting in a denial-of-service condition. An attacker with a crafted binary could cause a denial of service when the tool is integrated on a service pipeline.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31053.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31053
- https://github.com/rizinorg/rizin/issues/5753
- https://github.com/rizinorg/rizin/pull/5795
