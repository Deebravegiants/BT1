# [C] CVE-2021-43299

## Summary
Severity: Critical
Advisory: CVE-2021-43299
Aliases: CVE-2021-43300, CVE-2021-43301, CVE-2021-43302, CVE-2021-43303, GHSA-qcvw-h34v-c7r9
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/CVE-2021-43299
Type: osv

## Details
Stack overflow in PJSUA API when calling pjsua_player_create. An attacker-controlled 'filename' argument may cause a buffer overflow since it is copied to a fixed-size stack buffer without any size validation.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00038.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00030.html
- https://lists.debian.org/debian-lts-announce/2022/03/msg00035.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00021.html
- https://www.debian.org/security/2022/dsa-5285
- https://github.com/pjsip/pjproject/security/advisories/GHSA-qcvw-h34v-c7r9
