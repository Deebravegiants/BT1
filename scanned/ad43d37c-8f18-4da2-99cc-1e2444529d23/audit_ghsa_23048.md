# [H] IPython Notebook vulnerable to improper validation of the origin of websocket requests 

## Summary
Severity: High
Advisory: GHSA-75cw-5cgv-g853
CVE: CVE-2014-3429
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-75cw-5cgv-g853
Type: github-advisory

## Affected
- PyPI: `ipython` — affected >=0.12 <1.2.0

## Details
IPython Notebook 0.12 through 1.x before 1.2.0 does not validate the origin of websocket requests, which allows remote attackers to execute arbitrary code by leveraging knowledge of the kernel id and a crafted page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3429
- https://github.com/ipython/ipython/pull/4845
- https://github.com/ipython/ipython/commit/e5b669ce4750d628dba383fd637dbde918ea15f5
- https://github.com/mattvonrocketstein/ipython/commit/dd4135db9f42d196a46553310a8e63ff5658671d
- https://bugzilla.redhat.com/show_bug.cgi?id=1119890
- https://exchange.xforce.ibmcloud.com/vulnerabilities/94497
- https://github.com/ipython/ipython
- https://github.com/pypa/advisory-database/tree/main/vulns/ipython/PYSEC-2014-21.yaml
- http://advisories.mageia.org/MGASA-2014-0320.html
- http://lambdaops.com/cross-origin-websocket-hijacking-of-ipython
- http://lists.opensuse.org/opensuse-updates/2014-08/msg00039.html
- http://permalink.gmane.org/gmane.comp.python.ipython.devel/13198
- http://seclists.org/oss-sec/2014/q3/152
