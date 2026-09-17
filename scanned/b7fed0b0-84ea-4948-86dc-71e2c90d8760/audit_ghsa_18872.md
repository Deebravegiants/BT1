# [M] Synapse's invalid device keys degrade federation functionality

## Summary
Severity: Medium
Advisory: GHSA-fh66-fcv5-jjfr
CVE: CVE-2025-61672
CWE: CWE-1287
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-fh66-fcv5-jjfr
Type: github-advisory

## Affected
- PyPI: `matrix-synapse` — affected >=0 <1.138.3
- PyPI: `matrix-synapse` — affected >=1.139.0rc2 <1.139.1

## Details
### Impact

Lack of validation for device keys in Synapse before 1.138.3 and in Synapse 1.139.0 allow an attacker registered on the victim homeserver to degrade federation functionality, unpredictably breaking outbound federation to other homeservers. 

### Patches

Patched in Synapse 1.138.3, 1.138.4, 1.139.1, and 1.139.2.

Note that even though 1.138.3 and 1.139.1 fix the vulnerability, they inadvertently introduced an unrelated regression. For this reason, it is recommend to skip these releases and upgrading straight to 1.138.4 and 1.139.2.

### Workarounds

The vulnerability can only be exploited by users registered on the victim homeserver.

## References
- https://github.com/element-hq/synapse/security/advisories/GHSA-fh66-fcv5-jjfr
- https://nvd.nist.gov/vuln/detail/CVE-2025-61672
- https://github.com/element-hq/synapse/pull/17097
- https://github.com/element-hq/synapse/commit/26aaaf9e48fff80cf67a20c691c75d670034b3c1
- https://github.com/element-hq/synapse/commit/7069636c2d6d1ef2022287addf3ed8b919ef2740
- https://github.com/element-hq/synapse
- https://github.com/element-hq/synapse/releases/tag/v1.138.3
- https://github.com/element-hq/synapse/releases/tag/v1.138.4
- https://github.com/element-hq/synapse/releases/tag/v1.139.1
- https://github.com/element-hq/synapse/releases/tag/v1.139.2
