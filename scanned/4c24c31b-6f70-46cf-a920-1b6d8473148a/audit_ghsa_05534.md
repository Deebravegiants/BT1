# [H] Salt junos Module Vulnerable to Code Injection via Specially Crafted YAML Payload

## Summary
Severity: High
Advisory: GHSA-77w2-v593-vxvv
CVE: CVE-2025-62348
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-01-30
Source: https://github.com/advisories/GHSA-77w2-v593-vxvv
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3006.17

## Details
Salt's junos execution module contained an unsafe YAML decode/load usage. A specially crafted YAML payload processed by the junos module could lead to unintended code execution under the context of the Salt process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-62348
- https://github.com/saltstack/salt/issues/68469
- https://github.com/saltstack/salt/pull/68472/commits/c17fd645edef208233dcac855615fced69409a00
- https://docs.saltproject.io/en/latest/topics/releases/3006.17.html
- https://github.com/saltstack/salt
