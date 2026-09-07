# [C] Gerapy may cause remote code execution

## Summary
Severity: Critical
Advisory: GHSA-9w7f-m4j4-j3xw
CVE: CVE-2021-43857
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-9w7f-m4j4-j3xw
Type: github-advisory

## Affected
- PyPI: `gerapy` — affected >=0 <0.9.8

## Details
### Impact

project_configure function exist remote code execute in Gerapy < 0.9.8

### Patches

Patched in version 0.9.8, please install with:

```
pip3 install -U gerapy
```

## References
- https://github.com/Gerapy/Gerapy/security/advisories/GHSA-9w7f-m4j4-j3xw
- https://nvd.nist.gov/vuln/detail/CVE-2021-43857
- https://github.com/Gerapy/Gerapy/issues/219
- https://github.com/Gerapy/Gerapy/commit/49bcb19be5e0320e7e1535f34fe00f16a3cf3b28
- https://github.com/Gerapy/Gerapy
- https://github.com/pypa/advisory-database/tree/main/vulns/gerapy/PYSEC-2021-867.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/gerapy/PYSEC-2022-228.yaml
- http://packetstormsecurity.com/files/165459/Gerapy-0.9.7-Remote-Code-Execution.html
