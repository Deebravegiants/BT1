# [M] Using default SSLContext for HTTPS requests in an HTTPS proxy doesn't verify certificate hostname for proxy connection

## Summary
Severity: Medium
Advisory: GHSA-5phf-pp7p-vc2r
CVE: CVE-2021-28363
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-03-19
Source: https://github.com/advisories/GHSA-5phf-pp7p-vc2r
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=1.26.0 <1.26.4

## Details
### Impact

Users who are using an HTTPS proxy to issue HTTPS requests and haven't configured their own SSLContext via `proxy_config`.
Only the default SSLContext is impacted.

### Patches

[urllib3 >=1.26.4 has the issue resolved](https://github.com/urllib3/urllib3/releases/tag/1.26.4). urllib3<1.26 is not impacted due to not supporting HTTPS requests via HTTPS proxies.

### Workarounds

Upgrading is recommended as this is a minor release and not likely to break current usage.

Configuring an `SSLContext` with `check_hostname=True` and passing via `proxy_config` instead of relying on the default `SSLContext`

### For more information
If you have any questions or comments about this advisory:
* Email us at [sethmichaellarson@gmail.com](mailto:sethmichaellarson@gmail.com)

## References
- https://github.com/urllib3/urllib3/security/advisories/GHSA-5phf-pp7p-vc2r
- https://nvd.nist.gov/vuln/detail/CVE-2021-28363
- https://github.com/urllib3/urllib3/commit/8d65ea1ecf6e2cdc27d42124e587c1b83a3118b0
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2021-59.yaml
- https://github.com/pypa/advisory-db/tree/main/vulns/urllib3/PYSEC-2021-59.yaml
- https://github.com/urllib3/urllib3
- https://github.com/urllib3/urllib3/blob/main/CHANGES.rst#1264-2021-03-15
- https://github.com/urllib3/urllib3/commits/main
- https://github.com/urllib3/urllib3/releases/tag/1.26.4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4S65ZQVZ2ODGB52IC7VJDBUK4M5INCXL
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4S65ZQVZ2ODGB52IC7VJDBUK4M5INCXL
- https://pypi.org/project/urllib3/1.26.4
- https://security.gentoo.org/glsa/202107-36
- https://security.gentoo.org/glsa/202305-02
- https://security.netapp.com/advisory/ntap-20240621-0007
- https://www.oracle.com/security-alerts/cpuoct2021.html
