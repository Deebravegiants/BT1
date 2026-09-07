# [H] Logic error in authentication in proxy.py

## Summary
Severity: High
Advisory: GHSA-cmc7-mfmr-xqrx
CVE: CVE-2021-3116
CWE: CWE-287, CWE-480, CWE-697
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-04-07
Source: https://github.com/advisories/GHSA-cmc7-mfmr-xqrx
Type: github-advisory

## Affected
- PyPI: `proxy.py` — affected >=0 <2.3.1

## Details
before_upstream_connection in AuthPlugin in http/proxy/auth.py in proxy.py before 2.3.1 accepts incorrect Proxy-Authorization header data because of a boolean confusion (and versus or).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3116
- https://github.com/abhinavsingh/proxy.py/pull/482
- https://github.com/abhinavsingh/proxy.py/pull/482/commits/9b00093288237f5073c403f2c4f62acfdfa8ed46
- https://github.com/abhinavsingh/proxy.py/commit/bff171ec26d826ae1d22d2466eaf9d8bdbf059d3
- https://cardaci.xyz/advisories/2021/01/10/proxy.py-2.3.0-broken-basic-authentication
- https://github.com/abhinavsingh/proxy.py
- https://github.com/advisories/GHSA-cmc7-mfmr-xqrx
- https://github.com/pypa/advisory-database/tree/main/vulns/proxy-py/PYSEC-2021-46.yaml
- https://pypi.org/project/proxy.py/2.3.1/#history
