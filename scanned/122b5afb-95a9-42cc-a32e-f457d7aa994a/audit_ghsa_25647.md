# [H] Sensitive Auth & Cookie data stored in Jupyter server logs

## Summary
Severity: High
Advisory: GHSA-m87f-39q9-6f55
CVE: CVE-2022-24758
CWE: CWE-532
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-04-05
Source: https://github.com/advisories/GHSA-m87f-39q9-6f55
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <6.4.10

## Details
Anytime a 5xx error is triggered, the auth cookie and other header values are recorded in Jupyter server logs by default. Considering these logs do not require root access, an attacker can monitor these logs, steal sensitive auth/cookie information, and gain access to the Jupyter server.

Upgrade to notebook version 6.4.10

### For more information

If you have any questions or comments about this advisory, or vulnerabilities to report, please email our security list [security@ipython.org](mailto:security@ipython.org).

Credit: @3coins for reporting. Thank you!

## References
- https://github.com/jupyter/notebook/security/advisories/GHSA-m87f-39q9-6f55
- https://nvd.nist.gov/vuln/detail/CVE-2022-24758
- https://github.com/jupyter/notebook
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2022-180.yaml
