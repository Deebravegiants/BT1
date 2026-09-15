# [C] Roundcube Webmail Vulnerable to Authenticated RCE via PHP Object Deserialization

## Summary
Severity: Critical
Advisory: GHSA-8j8w-wwqc-x596
CVE: CVE-2025-49113
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-06-02
Source: https://github.com/advisories/GHSA-8j8w-wwqc-x596
Type: github-advisory

## Affected
- Packagist: `roundcube/roundcubemail` — affected >=0 <1.5.10
- Packagist: `roundcube/roundcubemail` — affected >=1.6.0 <1.6.11

## Details
Roundcube Webmail before 1.5.10 and 1.6.x before 1.6.11 allows remote code execution by authenticated users because the _from parameter in a URL is not validated in program/actions/settings/upload.php, leading to PHP Object Deserialization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-49113
- https://github.com/roundcube/roundcubemail/pull/9865
- https://github.com/roundcube/roundcubemail/commit/0376f69e958a8fef7f6f09e352c541b4e7729c4d
- https://github.com/roundcube/roundcubemail/commit/7408f31379666124a39f9cb1018f62bc5e2dc695
- https://github.com/roundcube/roundcubemail/commit/c50a07d88ca38f018a0f4a0b008e9a1deb32637e
- https://fearsoff.org/research/roundcube
- https://github.com/roundcube/roundcubemail
- https://github.com/roundcube/roundcubemail/releases/tag/1.5.10
- https://github.com/roundcube/roundcubemail/releases/tag/1.6.11
- https://lists.debian.org/debian-lts-announce/2025/06/msg00008.html
- https://roundcube.net/news/2025/06/01/security-updates-1.6.11-and-1.5.10
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-49113
- https://www.vicarius.io/vsociety/posts/cve-2025-49113-roundcube-mitigation-script
- https://www.vicarius.io/vsociety/posts/cve-2025-49113-roundcube-vulnerability-detection
- http://www.openwall.com/lists/oss-security/2025/06/02/3
