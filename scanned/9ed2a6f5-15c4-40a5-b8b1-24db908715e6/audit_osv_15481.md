# [M] CVE-2019-16723

## Summary
Severity: Medium
Advisory: CVE-2019-16723
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-09-23
Source: https://osv.dev/vulnerability/CVE-2019-16723
Type: osv

## Details
In Cacti through 1.2.6, authenticated users may bypass authorization checks (for viewing a graph) via a direct graph_json.php request with a modified local_graph_id parameter.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00048.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZO3ROHHPKLH2JRW7ES5FYSQTWIPNVLQB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZSCUUCKSYVZLN3PQE7NU76AFWUGT3E2D/
- https://seclists.org/bugtraq/2020/Jan/25
- https://security.gentoo.org/glsa/202003-40
- https://www.debian.org/security/2020/dsa-4604
- https://github.com/Cacti/cacti/issues/2964
