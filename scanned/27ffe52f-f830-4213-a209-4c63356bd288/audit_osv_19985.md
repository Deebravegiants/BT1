# [H] CVE-2021-28905

## Summary
Severity: High
Advisory: CVE-2021-28905
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-28905
Type: osv

## Details
In function lys_node_free() in libyang <= v1.0.225, it asserts that the value of node->module can't be NULL. But in some cases, node->module can be null, which triggers a reachable assertion (CWE-617).

## References
- https://security.gentoo.org/glsa/202107-54
- https://github.com/CESNET/libyang/issues/1452
