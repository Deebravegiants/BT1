# [M] CVE-2021-31924

## Summary
Severity: Medium
Advisory: CVE-2021-31924
CVSS: 6.8 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-31924
Type: osv

## Details
Yubico pam-u2f before 1.1.1 has a logic issue that, depending on the pam-u2f configuration and the application used, could lead to a local PIN bypass. This issue does not allow user presence (touch) or cryptographic signature verification to be bypassed, so an attacker would still need to physically possess and interact with the YubiKey or another enrolled authenticator. If pam-u2f is configured to require PIN authentication, and the application using pam-u2f allows the user to submit NULL as the PIN, pam-u2f will attempt to perform a FIDO2 authentication without PIN. If this authentication is successful, the PIN requirement is bypassed.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CRBVOZEMVO72FV4Z5O4GBGSURXHWRGD3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IL3I5AKECLMK4ADLLACLOEF7H5CMNDP2/
- https://developers.yubico.com/pam-u2f/
- https://security.gentoo.org/glsa/202208-11
- https://www.yubico.com/support/security-advisories/ysa-2021-03
