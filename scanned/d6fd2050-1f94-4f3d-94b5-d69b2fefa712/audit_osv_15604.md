# [H] CVE-2019-17566

## Summary
Severity: High
Advisory: CVE-2019-17566
Aliases: GHSA-cmx4-p4v5-hmr5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-11-12
Source: https://osv.dev/vulnerability/CVE-2019-17566
Type: osv

## Details
Apache Batik is vulnerable to server-side request forgery, caused by improper input validation by the "xlink:href" attributes. By using a specially-crafted argument, an attacker could exploit this vulnerability to cause the underlying server to make arbitrary GET requests.

## References
- https://lists.apache.org/thread.html/rab94fe68b180d2e2fba97abf6fe1ec83cff826be25f86cd90f047171%40%3Ccommits.myfaces.apache.org%3E
- https://lists.apache.org/thread.html/rcab14a9ec91aa4c151e0729966282920423eff50a22759fd21db6509%40%3Ccommits.myfaces.apache.org%3E
- https://security.gentoo.org/glsa/202401-11
- https://xmlgraphics.apache.org/security.html
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
