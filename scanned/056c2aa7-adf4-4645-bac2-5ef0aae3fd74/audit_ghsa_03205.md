# [M] Prevent user enumeration using Guard or the new Authenticator-based Security

## Summary
Severity: Medium
Advisory: GHSA-5pv8-ppvj-4h68
CVE: CVE-2021-21424
CWE: CWE-200, CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-05-13
Source: https://github.com/advisories/GHSA-5pv8-ppvj-4h68
Type: github-advisory

## Affected
- Packagist: `symfony/security` — affected >=5.0.0 <5.2.8
- Packagist: `symfony/security-guard` — affected >=2.8.0 <3.4.48
- Packagist: `symfony/security-guard` — affected >=4.0.0 <4.4.23
- Packagist: `symfony/security-guard` — affected >=5.0.0 <5.2.8
- Packagist: `symfony/security-core` — affected >=2.8.0 <3.4.48
- Packagist: `symfony/security-core` — affected >=4.0.0 <4.4.23
- Packagist: `symfony/security-core` — affected >=5.0.0 <5.2.8
- Packagist: `lexik/jwt-authentication-bundle` — affected >=2.0.0 <2.10.7
- Packagist: `lexik/jwt-authentication-bundle` — affected >=2.11.0 <2.11.3
- Packagist: `symfony/maker-bundle` — affected >=1.27.0 <1.29.2
- Packagist: `symfony/maker-bundle` — affected >=1.30.0 <1.31.1
- Packagist: `symfony/security-http` — affected >=5.1.0 <5.2.8
- Packagist: `symfony/security` — affected >=2.8.0 <3.4.49
- Packagist: `symfony/security` — affected >=4.0.0 <4.4.24
- Packagist: `symfony/symfony` — affected >=2.8.0 <3.4.49
- Packagist: `symfony/symfony` — affected >=4.0.0 <4.4.24
- Packagist: `symfony/symfony` — affected >=5.0.0 <5.2.9

## Details
Description
-----------

The ability to enumerate users was possible without relevant permissions due to different exception messages depending on whether the user existed or not. It was also possible to enumerate users by using a timing attack, by comparing time elapsed when authenticating an existing user and authenticating a non-existing user.

Resolution
----------

We now ensure that 403s are returned whether the user exists or not if the password is invalid or if the user does not exist.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/2a581d22cc621b33d5464ed65c4bc2057f72f011) for branch 3.4.

Credits
-------

I would like to thank James Isaac and Mathias Brodala for reporting the issue and Robin Chalas for fixing the issue.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-5pv8-ppvj-4h68
- https://nvd.nist.gov/vuln/detail/CVE-2021-21424
- https://github.com/symfony/symfony/commit/2a581d22cc621b33d5464ed65c4bc2057f72f011
- https://symfony.com/cve-2021-21424
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VRUS2H2SSOQWNLBD35SKIWIDQEMV2PD3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UC7BND775DVZDQT3RMGD2HVB2PKLJDJW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RH7TMM5CHQYBFFGXWRPJDPB3SKCZXI2M
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KENRNLB3FYXYGDWRBH2PDBOZZKOD7VY4
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VRUS2H2SSOQWNLBD35SKIWIDQEMV2PD3
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UC7BND775DVZDQT3RMGD2HVB2PKLJDJW
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RH7TMM5CHQYBFFGXWRPJDPB3SKCZXI2M
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KENRNLB3FYXYGDWRBH2PDBOZZKOD7VY4
- https://lists.debian.org/debian-lts-announce/2023/07/msg00014.html
- https://github.com/symfony/symfony
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2021-21424.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security/CVE-2021-21424.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2021-21424.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-guard/CVE-2021-21424.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/maker-bundle/CVE-2021-21424.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/lexik/jwt-authentication-bundle/CVE-2021-21424.yaml
