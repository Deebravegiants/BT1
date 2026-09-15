# [M] Zope allows attackers to modify raw image and file data

## Summary
Severity: Medium
Advisory: GHSA-7whr-j8vf-r4wj
CVE: CVE-2000-1212
CWE: CWE-284
Ecosystem: PyPI
Published: 2022-04-30
Source: https://github.com/advisories/GHSA-7whr-j8vf-r4wj
Type: github-advisory

## Affected
- PyPI: `zope` — affected >=2.2.0

## Details
Zope 2.2.0 through 2.2.4 does not properly protect a data updating method on Image and File objects, which allows attackers with DTML editing privileges to modify the raw data of these objects.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2000-1212
- https://exchange.xforce.ibmcloud.com/vulnerabilities/5778
- https://web.archive.org/web/20020117134418/http://distro.conectiva.com.br/atualizacoes/?id=a&anuncio=000365
- http://www.debian.org/security/2001/dsa-007
- http://www.redhat.com/support/errata/RHSA-2000-135.html
- http://www.zope.org/Products/Zope/Hotfix_2000-12-18/security_alert
