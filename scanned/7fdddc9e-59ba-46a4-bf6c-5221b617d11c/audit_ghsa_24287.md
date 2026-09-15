# [C] Improper Input Validation in Jupyter Notebook

## Summary
Severity: Critical
Advisory: GHSA-92mr-v722-f48m
CVE: CVE-2015-7337
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-92mr-v722-f48m
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=4.0.0 <4.0.5
- PyPI: `ipython` — affected >=0 <3.2.2

## Details
The editor in IPython Notebook before 3.2.2 and Jupyter Notebook 4.0.x before 4.0.5 allows remote attackers to execute arbitrary JavaScript code via a crafted file, which triggers a redirect to files/, related to MIME types.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7337
- https://github.com/ipython/ipython/commit/0a8096adf165e2465550bd5893d7e352544e5967
- https://github.com/jupyter/notebook/commit/9e63dd89b603dfbe3a7e774d8a962ee0fa30c0b5
- https://bugzilla.redhat.com/show_bug.cgi?id=1264067
- https://github.com/advisories/GHSA-92mr-v722-f48m
- https://github.com/pypa/advisory-database/tree/main/vulns/ipython/PYSEC-2015-25.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2015-27.yaml
- https://security.gentoo.org/glsa/201512-02
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/167670.html
- http://seclists.org/oss-sec/2015/q3/558
- http://seclists.org/oss-sec/2015/q3/634
