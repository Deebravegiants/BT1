# [M] CVE-2020-28463

## Summary
Severity: Medium
Advisory: CVE-2020-28463
Aliases: GHSA-mpvw-25mg-59vx, PYSEC-2021-146, SNYK-PYTHON-REPORTLAB-1022145
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-18
Source: https://osv.dev/vulnerability/CVE-2020-28463
Type: osv

## Details
All versions of package reportlab are vulnerable to Server-side Request Forgery (SSRF) via img tags. In order to reduce risk, use trustedSchemes & trustedHosts (see in Reportlab's documentation) Steps to reproduce by Karan Bamal: 1. Download and install the latest package of reportlab 2. Go to demos -> odyssey -> dodyssey 3. In the text file odyssey.txt that needs to be converted to pdf inject <img src="http://127.0.0.1:5000" valign="top"/> 4. Create a nc listener nc -lp 5000 5. Run python3 dodyssey.py 6. You will get a hit on your nc showing we have successfully proceded to send a server side request 7. dodyssey.py will show error since there is no img file on the url, but we are able to do SSRF

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YZQSFCID67K6BTC655EQY6MNOF35QI44/
- https://lists.debian.org/debian-lts-announce/2023/09/msg00037.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HMUJA5GZTPQ5WRYUCCK2GEZM4W43N7HH/
- https://www.reportlab.com/docs/reportlab-userguide.pdf
- https://snyk.io/vuln/SNYK-PYTHON-REPORTLAB-1022145
