# [H] CVE-2017-15114

## Summary
Severity: High
Advisory: CVE-2017-15114
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-15114
Type: osv

## Details
When libvirtd is configured by OSP director (tripleo-heat-templates) to use the TLS transport it defaults to the same certificate authority as all non-libvirtd services. As no additional authentication is configured this allows these services to connect to libvirtd (which is equivalent to root access). If a vulnerability exists in another service it could, combined with this flaw, be exploited to escalate privileges to gain control over compute nodes.

## References
- http://www.securityfocus.com/bid/101971
- https://git.openstack.org/cgit/openstack/tripleo-heat-templates/commit/?id=994922a8ba996fe68d047df0e1486fa805dbea31
