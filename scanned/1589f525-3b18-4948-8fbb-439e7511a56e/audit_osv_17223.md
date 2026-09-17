# [H] CVE-2020-13848

## Summary
Severity: High
Advisory: CVE-2020-13848
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-04
Source: https://osv.dev/vulnerability/CVE-2020-13848
Type: osv

## Details
Portable UPnP SDK (aka libupnp) 1.12.1 and earlier allows remote attackers to cause a denial of service (crash) via a crafted SSDP message due to a NULL pointer dereference in the functions FindServiceControlURLPath and FindServiceEventURLPath in genlib/service_table/service_table.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00033.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00007.html
- https://github.com/pupnp/pupnp/issues/177
- https://lists.debian.org/debian-lts-announce/2020/06/msg00006.html
- https://github.com/pupnp/pupnp/commit/c805c1de1141cb22f74c0d94dd5664bda37398e0
