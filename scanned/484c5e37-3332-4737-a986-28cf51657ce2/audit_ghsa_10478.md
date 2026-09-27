# [H] TorchGeo Remote Code Execution Vulnerability

## Summary
Severity: High
Advisory: GHSA-ghq9-vc6f-8qjf
CVE: CVE-2024-49048
CWE: CWE-94, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-ghq9-vc6f-8qjf
Type: github-advisory

## Affected
- PyPI: `torchgeo` — affected >=0.4 <0.6.1

## Details
### Impact

TorchGeo 0.4–0.6.0 used an [`eval`](https://docs.python.org/3/library/functions.html#eval) statement in its model weight API that could allow an unauthenticated, remote attacker to execute arbitrary commands. All platforms that expose [`torchgeo.models.get_weight()`](https://torchgeo.readthedocs.io/en/v0.6.0/api/models.html#torchgeo.models.get_weight) or [`torchgeo.trainers`](https://torchgeo.readthedocs.io/en/v0.6.0/api/trainers.html) as an external API could be affected.

### Patches

The `eval` statement was replaced with a fixed enum lookup, preventing arbitrary code injection. All users are encouraged to upgrade to TorchGeo 0.6.1 or newer.

### Workarounds

In unpatched versions, input validation and sanitization can be used to avoid this vulnerability.

### References

#### Bug history

* Introduced: https://github.com/torchgeo/torchgeo/pull/917
* Patched: https://github.com/torchgeo/torchgeo/pull/2323
* Released: [v0.6.1](https://github.com/microsoft/torchgeo/releases/tag/v0.6.1)

## References
- https://github.com/torchgeo/torchgeo/security/advisories/GHSA-ghq9-vc6f-8qjf
- https://nvd.nist.gov/vuln/detail/CVE-2024-49048
- https://github.com/torchgeo/torchgeo/pull/2323
- https://github.com/torchgeo/torchgeo/pull/917
- https://github.com/torchgeo/torchgeo/commit/1a980788cb7089a1115f3b786c7daa9dd47d7d7a
- https://github.com/microsoft/torchgeo/releases/tag/v0.6.1
- https://github.com/pypa/advisory-database/tree/main/vulns/torchgeo/PYSEC-2024-204.yaml
- https://github.com/torchgeo/torchgeo
- https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-49048
