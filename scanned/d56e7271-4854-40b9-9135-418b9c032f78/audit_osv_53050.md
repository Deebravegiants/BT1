# [H] CVE-2022-26490

## Summary
Severity: High
Advisory: CVE-2022-26490
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-03-06
Source: https://osv.dev/vulnerability/CVE-2022-26490
Type: osv

## Details
st21nfca_connectivity_event_received in drivers/nfc/st21nfca/se.c in the Linux kernel through 5.16.12 has EVT_TRANSACTION buffer overflows because of untrusted length parameters.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C5AUUDGSDLGYU7SZSK4PFAN22NISQZBT/
- https://security.netapp.com/advisory/ntap-20220429-0004/
- https://www.debian.org/security/2022/dsa-5127
- https://www.debian.org/security/2022/dsa-5173
- https://lists.debian.org/debian-lts-announce/2022/07/msg00000.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BG4J46EMFPDD5QHYXDUI3PJCZQ7HQAZR/
- https://github.com/torvalds/linux/commit/4fbcc1a4cb20fe26ad0225679c536c80f1648221
