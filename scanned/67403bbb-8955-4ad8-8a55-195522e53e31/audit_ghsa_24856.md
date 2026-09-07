# [M] Improper Neutralization of Input During Web Page Generation in JAMon

## Summary
Severity: Medium
Advisory: GHSA-qpr7-5m63-hq2c
CVE: CVE-2013-6235
CWE: CWE-79
Ecosystem: Maven
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qpr7-5m63-hq2c
Type: github-advisory

## Affected
- Maven: `com.jamonapi:jamon` — affected >=0 <2.80

## Details
Multiple cross-site scripting (XSS) vulnerabilities in JAMon (Java Application Monitor) 2.7 and earlier allow remote attackers to inject arbitrary web script or HTML via the (1) listenertype or (2) currentlistener parameter to mondetail.jsp or ArraySQL parameter to (3) mondetail.jsp, (4) jamonadmin.jsp, (5) sql.jsp, or (6) exceptions.jsp.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-6235
- https://exchange.xforce.ibmcloud.com/vulnerabilities/90699
- http://osvdb.org/102570
- http://osvdb.org/102571
- http://osvdb.org/102572
- http://osvdb.org/102573
- http://packetstormsecurity.com/files/124933
- http://seclists.org/fulldisclosure/2014/Jan/164
- http://www.securityfocus.com/archive/1/530877/100/0/threaded
