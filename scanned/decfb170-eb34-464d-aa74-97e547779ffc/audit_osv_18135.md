# [M] CVE-2020-24349

## Summary
Severity: Medium
Advisory: CVE-2020-24349
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-08-13
Source: https://osv.dev/vulnerability/CVE-2020-24349
Type: osv

## Details
njs through 0.4.3, used in NGINX, allows control-flow hijack in njs_value_property in njs_value.c. NOTE: the vendor considers the issue to be "fluff" in the NGINX use case because there is no remote attack surface.

## References
- https://cwe.mitre.org/data/definitions/416.html
- https://security.netapp.com/advisory/ntap-20200918-0001/
- https://github.com/nginx/njs/issues/324
