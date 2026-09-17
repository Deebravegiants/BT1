# [H] CVE-2021-28904

## Summary
Severity: High
Advisory: CVE-2021-28904
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-20
Source: https://osv.dev/vulnerability/CVE-2021-28904
Type: osv

## Details
In function ext_get_plugin() in libyang <= v1.0.225, it doesn't check whether the value of revision is NULL. If revision is NULL, the operation of strcmp(revision, ext_plugins[u].revision) will lead to a crash.

## References
- https://security.gentoo.org/glsa/202107-54
- https://github.com/CESNET/libyang/issues/1451
