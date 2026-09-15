# [M] CVE-2023-45866

## Summary
Severity: Medium
Advisory: CVE-2023-45866
Aliases: A-294854926, ASB-A-294854926
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-12-08
Source: https://osv.dev/vulnerability/CVE-2023-45866
Type: osv

## Details
Bluetooth HID Hosts in BlueZ may permit an unauthenticated Peripheral role HID Device to initiate and establish an encrypted connection, and accept HID keyboard reports, potentially permitting injection of HID messages when no user interaction has occurred in the Central role to authorize such access. An example affected package is bluez 5.64-0ubuntu1 in Ubuntu 22.04LTS. NOTE: in some cases, a CVE-2020-0556 mitigation would have already addressed this Bluetooth HID Hosts issue.

## References
- https://bluetooth.com
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D2N2P5LMP3V7IJONALV2KOFL4NUU23CJ/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/77YQQS5FXPYE6WBBZO3REFIRAUJHERFA/
- https://github.com/skysafe/reblog/tree/main/cve-2023-45866
- http://changelogs.ubuntu.com/changelogs/pool/main/b/bluez/bluez_5.64-0ubuntu1/changelog
- http://seclists.org/fulldisclosure/2023/Dec/7
- https://security.gentoo.org/glsa/202401-03
- https://support.apple.com/kb/HT214035
- https://www.debian.org/security/2023/dsa-5584
- http://seclists.org/fulldisclosure/2023/Dec/9
- https://lists.debian.org/debian-lts-announce/2023/12/msg00011.html
- https://support.apple.com/kb/HT214036
- https://git.kernel.org/pub/scm/bluetooth/bluez.git/commit/profiles/input?id=25a471a83e02e1effb15d5a488b3f0085eaeb675
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/77YQQS5FXPYE6WBBZO3REFIRAUJHERFA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/D2N2P5LMP3V7IJONALV2KOFL4NUU23CJ/
