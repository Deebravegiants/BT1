# [M] CVE-2019-20372

## Summary
Severity: Medium
Advisory: CVE-2019-20372
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-01-09
Source: https://osv.dev/vulnerability/CVE-2019-20372
Type: osv

## Details
NGINX before 1.17.7, with certain error_page configurations, allows HTTP request smuggling, as demonstrated by the ability of an attacker to read unauthorized web pages in environments where NGINX is being fronted by a load balancer.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00013.html
- http://nginx.org/en/CHANGES
- http://seclists.org/fulldisclosure/2021/Sep/36
- https://duo.com/docs/dng-notes#version-1.5.4-january-2020
- https://security.netapp.com/advisory/ntap-20200127-0003/
- https://support.apple.com/kb/HT212818
- https://usn.ubuntu.com/4235-1/
- https://usn.ubuntu.com/4235-2/
- https://github.com/kubernetes/ingress-nginx/pull/4859
- https://github.com/nginx/nginx/commit/c1be55f97211d38b69ac0c2027e6812ab8b1b94e
- https://bertjwregeer.keybase.pub/2019-12-10%20-%20error_page%20request%20smuggling.pdf
