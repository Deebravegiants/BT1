# [M] CVE-2020-26558

## Summary
Severity: Medium
Advisory: CVE-2020-26558
Aliases: A-174886838, ASB-A-174886838
CVSS: 4.2 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2021-05-24
Source: https://osv.dev/vulnerability/CVE-2020-26558
Type: osv

## Details
Bluetooth LE and BR/EDR secure pairing in Bluetooth Core Specification 2.1 through 5.2 may permit a nearby man-in-the-middle attacker to identify the Passkey used during pairing (in the Passkey authentication procedure) by reflection of the public key and the authentication evidence of the initiating device, potentially permitting this attacker to complete authenticated pairing with the responding device using the correct Passkey for the pairing session. The attack methodology determines the Passkey value one bit at a time.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NSS6CTGE4UGTJLCOZOASDR3T3SLL6QJZ/
- https://www.kb.cert.org/vuls/id/799380
- https://kb.cert.org/vuls/id/799380
- https://lists.debian.org/debian-lts-announce/2021/06/msg00019.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/06/msg00022.html
- https://security.gentoo.org/glsa/202209-16
- https://www.bluetooth.com/learn-about-bluetooth/key-attributes/bluetooth-security/reporting-security/
- https://www.debian.org/security/2021/dsa-4951
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00517.html
- https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00520.html
