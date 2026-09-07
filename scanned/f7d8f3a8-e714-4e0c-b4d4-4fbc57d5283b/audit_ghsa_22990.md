# [M] Improper Neutralization of Input During Web Page Generation in Jupyter Notebook

## Summary
Severity: Medium
Advisory: GHSA-4vwq-x64q-j4cj
CVE: CVE-2015-6938
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-4vwq-x64q-j4cj
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=4.0.0 <4.0.5
- PyPI: `ipython` — affected >=0 <3.2.2

## Details
Cross-site scripting (XSS) vulnerability in the file browser in notebook/notebookapp.py in IPython Notebook before 3.2.2 and Jupyter Notebook 4.0.x before 4.0.5 allows remote attackers to inject arbitrary web script or HTML via a folder name.  NOTE: this was originally reported as a cross-site request forgery (CSRF) vulnerability, but this may be inaccurate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-6938
- https://github.com/ipython/ipython/commit/3ab41641cf6fce3860c73d5cf4645aa12e1e5892
- https://github.com/jupyter/notebook/commit/35f32dd2da804d108a3a3585b69ec3295b2677ed
- https://github.com/jupyter/notebook/commit/dd9876381f0ef09873d8c5f6f2063269172331e3
- https://bugzilla.redhat.com/show_bug.cgi?id=1259405
- https://github.com/advisories/GHSA-4vwq-x64q-j4cj
- https://github.com/pypa/advisory-database/tree/main/vulns/ipython/PYSEC-2015-24.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2015-26.yaml
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/166460.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/166471.html
- http://lists.fedoraproject.org/pipermail/package-announce/2015-September/167670.html
- http://lists.opensuse.org/opensuse-updates/2015-10/msg00016.html
- http://seclists.org/oss-sec/2015/q3/474
- http://seclists.org/oss-sec/2015/q3/544
