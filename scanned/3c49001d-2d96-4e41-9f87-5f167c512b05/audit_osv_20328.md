# [H] CVE-2021-32800

## Summary
Severity: High
Advisory: CVE-2021-32800
Aliases: GHSA-gv5w-8q25-785v
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-32800
Type: osv

## Details
Nextcloud server is an open source, self hosted personal cloud. In affected versions an attacker is able to bypass Two Factor Authentication in Nextcloud. Thus knowledge of a password, or access to a WebAuthN trusted device of a user was sufficient to gain access to an account. It is recommended that the Nextcloud Server is upgraded to 20.0.12, 21.0.4 or 22.1.0. There are no workaround for this vulnerability.

## References
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-gv5w-8q25-785v
- https://security.gentoo.org/glsa/202208-17
- https://hackerone.com/reports/1271052
- https://github.com/nextcloud/server/pull/28078
