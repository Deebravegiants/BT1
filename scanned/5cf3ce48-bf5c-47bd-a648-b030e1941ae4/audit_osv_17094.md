# [C] CVE-2020-12274

## Summary
Severity: Critical
Advisory: CVE-2020-12274
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-27
Source: https://osv.dev/vulnerability/CVE-2020-12274
Type: osv

## Details
In TestLink 1.9.20, the lib/cfields/cfieldsExport.php goback_url parameter causes a security risk because it depends on client input and is not constrained to lib/cfields/cfieldsView.php at the web site associated with the session.

## References
- http://mantis.testlink.org/view.php?id=8894
- https://github.com/TestLinkOpenSourceTRMS/testlink-code/commit/2d17cd00f981f8e8c97de34a12e368ba2a55e3d0
