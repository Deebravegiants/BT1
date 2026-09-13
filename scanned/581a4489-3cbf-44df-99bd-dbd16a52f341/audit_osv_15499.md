# [C] CVE-2019-16885

## Summary
Severity: Critical
Advisory: CVE-2019-16885
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-03
Source: https://osv.dev/vulnerability/CVE-2019-16885
Type: osv

## Details
In OkayCMS through 2.3.4, an unauthenticated attacker can achieve remote code execution by injecting a malicious PHP object via a crafted cookie. This could happen at two places: first in view/ProductsView.php using the cookie price_filter, and second in api/Comparison.php via the cookie comparison.

## References
- http://packetstormsecurity.com/files/155583/OkayCMS-2.3.4-Remote-Code-Execution.html
- http://seclists.org/fulldisclosure/2019/Dec/15
- https://www.ait.ac.at/ait-sa-20191129-01-unauthenticated-remote-code-execution-okaycms
