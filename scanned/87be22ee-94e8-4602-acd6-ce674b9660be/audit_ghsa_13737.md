# [H] Remarshal expands YAML alias nodes unlimitedly, hence Remarshal is vulnerable to Billion Laughs Attack

## Summary
Severity: High
Advisory: GHSA-gw7g-qr8w-3448
CVE: CVE-2023-47163
CWE: CWE-400, CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-13
Source: https://github.com/advisories/GHSA-gw7g-qr8w-3448
Type: github-advisory

## Affected
- PyPI: `remarshal` — affected >=0 <0.17.1

## Details
Remarshal prior to v0.17.1 expands YAML alias nodes unlimitedly, hence Remarshal is vulnerable to Billion Laughs Attack. Processing untrusted YAML files may cause a denial-of-service (DoS) condition.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-47163
- https://github.com/remarshal-project/remarshal/commit/fd6ac799a02f533c3fc243b49cdd6d21aa7ee494
- https://github.com/pypa/advisory-database/tree/main/vulns/remarshal/PYSEC-2023-236.yaml
- https://github.com/remarshal-project/remarshal
- https://github.com/remarshal-project/remarshal/releases/tag/v0.17.1
- https://jvn.jp/en/jp/JVN86156389
