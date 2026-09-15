# [M] CVE-2020-11023

## Summary
Severity: Medium
Advisory: CVE-2020-11023
Aliases: BIT-drupal-2020-11023, GHSA-jpcq-cgw6-v4j6
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-04-29
Source: https://osv.dev/vulnerability/CVE-2020-11023
Type: osv

## Details
In jQuery versions greater than or equal to 1.0.3 and before 3.5.0, passing HTML containing <option> elements from untrusted sources - even after sanitizing it - to one of jQuery's DOM manipulation methods (i.e. .html(), .append(), and others) may execute untrusted code. This problem is patched in jQuery 3.5.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00085.html
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-11023
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00039.html
- https://blog.jquery.com/2020/04/10/jquery-3-5-0-released
- https://github.com/github/advisory-database/blob/99afa6fdeaf5d1d23e1021ff915a5e5dbc82c1f1/advisories/github-reviewed/2020/04/GHSA-jpcq-cgw6-v4j6/GHSA-jpcq-cgw6-v4j6.json#L20-L37
- https://github.com/jquery/jquery/security/advisories/GHSA-jpcq-cgw6-v4j6
- https://jquery.com/upgrade-guide/3.5/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00033.html
- https://lists.debian.org/debian-lts-announce/2023/08/msg00040.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AVKYXLWCLZBV2N7M46KYK4LVA5OXWPBY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QPN2L2XVQGUA2V5HNQJWHK3APSK3VN7K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SAPQVX3XDNPGFT26QAQ6AJIXZZBZ4CD4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SFP4UK4EGP4AFH2MWYJ5A5Z4I7XVFQ6B/
- https://security.gentoo.org/glsa/202007-03
- https://security.netapp.com/advisory/ntap-20200511-0006/
- https://www.debian.org/security/2020/dsa-4693
- https://www.drupal.org/sa-core-2020-002
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujul2020.html
