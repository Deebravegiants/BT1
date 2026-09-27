# [C] graphite-web is vulnerable to Remote Code Execution via renderLocalView function 

## Summary
Severity: Critical
Advisory: GHSA-m923-w2gj-v43g
CVE: CVE-2013-5093
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-m923-w2gj-v43g
Type: github-advisory

## Affected
- PyPI: `graphite-web` — affected >=0.9.5 <0.9.11

## Details
The renderLocalView function in render/views.py in graphite-web in Graphite 0.9.5 through 0.9.10 uses the pickle Python module unsafely, which allows remote attackers to execute arbitrary code via a crafted serialized object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-5093
- https://github.com/graphite-project/graphite-web
- https://github.com/graphite-project/graphite-web/blob/d39d455622127e479d8c4e7760311e3883cfd086/docs/releases/0_9_11.rst
- https://github.com/graphite-project/graphite-web/blob/master/docs/releases/0_9_11.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/graphite-web/PYSEC-2013-3.yaml
- https://github.com/rapid7/metasploit-framework/blob/master/modules/exploits/unix/webapp/graphite_pickle_exec.rb
- https://web.archive.org/web/20200228174538/http://www.securityfocus.com/bid/61894
- http://ceriksen.com/2013/08/20/graphite-remote-code-execution-vulnerability-advisory
- http://www.exploit-db.com/exploits/27752
