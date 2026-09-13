# [H] Jupyter server on Windows discloses Windows user password hash

## Summary
Severity: High
Advisory: GHSA-hrw6-wg82-cm62
CVE: CVE-2024-35178
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-hrw6-wg82-cm62
Type: github-advisory

## Affected
- PyPI: `jupyter_server` — affected >=0 <2.14.1

## Details
### Summary

Jupyter Server on Windows has a vulnerability that lets unauthenticated attackers leak the NTLMv2 password hash of the Windows user running the Jupyter server. An attacker can crack this password to gain access to the Windows machine hosting the Jupyter server, or access other network-accessible machines or 3rd party services using that credential. Or an attacker perform an NTLM relay attack without cracking the credential to gain access to other network-accessible machines.

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-hrw6-wg82-cm62
- https://nvd.nist.gov/vuln/detail/CVE-2024-35178
- https://github.com/jupyter-server/jupyter_server/commit/79fbf801c5908f4d1d9bc90004b74cfaaeeed2df
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2024-165.yaml
