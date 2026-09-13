# [H] Execution with Unnecessary Privileges in JupyterApp

## Summary
Severity: High
Advisory: GHSA-m678-f26j-3hrp
CVE: CVE-2022-39286
CWE: CWE-250, CWE-269, CWE-427
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-26
Source: https://github.com/advisories/GHSA-m678-f26j-3hrp
Type: github-advisory

## Affected
- PyPI: `jupyter-core` — affected >=0 <4.11.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
We’d like to disclose an arbitrary code execution vulnerability in `jupyter_core` that stems from `jupyter_core` executing untrusted files in the current working directory. This vulnerability allows one user to run code as another.


### Patches
_Has the problem been patched? What versions should users upgrade to?_
Users should upgrade to `jupyter_core>=4.11.2`.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
No

### References
_Are there any links users can visit to find out more?_
Similar advisory in [IPython](https://github.com/advisories/GHSA-pq7m-3gw7-gq5x)

## References
- https://github.com/jupyter/jupyter_core/security/advisories/GHSA-m678-f26j-3hrp
- https://nvd.nist.gov/vuln/detail/CVE-2022-39286
- https://github.com/jupyter/jupyter_core/commit/1118c8ce01800cb689d51f655f5ccef19516e283
- https://github.com/jupyter/jupyter_core
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-core/PYSEC-2022-42974.yaml
- https://lists.debian.org/debian-lts-announce/2022/11/msg00022.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KKMP5OXXIX2QAUNVNJZ5UEQFKDYYJVBA
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/YIDN7JMLK6AOMBQI4QPSW4MBQGWQ5NIN
- https://security.gentoo.org/glsa/202301-04
- https://www.debian.org/security/2023/dsa-5422
