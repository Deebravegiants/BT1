# [C] Incomplete List of Disallowed Inputs in SOFA-Hessian

## Summary
Severity: Critical
Advisory: GHSA-pfwp-8pq4-g7pv
CVE: CVE-2019-9212
CWE: CWE-184, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-03-06
Source: https://github.com/advisories/GHSA-pfwp-8pq4-g7pv
Type: github-advisory

## Affected
- Maven: `com.alipay.sofa:hessian` — affected >=4.0.0 <4.0.2
- Maven: `com.alipay.sofa:hessian` — affected >=0 <3.3.6

## Details
SOFA-Hessian through 4.0.2 allows remote attackers to execute arbitrary commands via a crafted serialized Hessian object because blacklisting of com.caucho.naming.QName and com.sun.org.apache.xpath.internal.objects.XString is mishandled, related to Resin Gadget.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-9212
- https://github.com/alipay/sofa-hessian/issues/34
- https://github.com/advisories/GHSA-pfwp-8pq4-g7pv
- https://github.com/alipay/sofa-hessian
