# [C] CVE-2016-2563

## Summary
Severity: Critical
Advisory: CVE-2016-2563
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-07
Source: https://osv.dev/vulnerability/CVE-2016-2563
Type: osv

## Details
Stack-based buffer overflow in the SCP command-line utility in PuTTY before 0.67 and KiTTY 0.66.6.3 and earlier allows remote servers to cause a denial of service (stack memory corruption) or execute arbitrary code via a crafted SCP-SINK file-size response to an SCP download request.

## References
- http://seclists.org/fulldisclosure/2016/Mar/22
- http://www.securityfocus.com/bid/84296
- http://www.securitytracker.com/id/1035257
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00131.html
- https://github.com/tintinweb/pub/tree/master/pocs/cve-2016-2563
- https://security.gentoo.org/glsa/201606-01
- http://www.chiark.greenend.org.uk/~sgtatham/putty/wishlist/vuln-pscp-sink-sscanf.html
