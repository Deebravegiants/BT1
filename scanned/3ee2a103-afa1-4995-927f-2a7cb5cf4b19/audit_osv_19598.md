# [M] CVE-2021-22570

## Summary
Severity: Medium
Advisory: CVE-2021-22570
Aliases: GHSA-77rm-9x9h-xj3g, PYSEC-2022-48
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-01-26
Source: https://osv.dev/vulnerability/CVE-2021-22570
Type: osv

## Details
Nullptr dereference when a null char is present in a proto symbol. The symbol is parsed incorrectly, leading to an unchecked call into the proto file's name during generation of the resulting error message. Since the symbol is incorrectly parsed, the file is nullptr. We recommend upgrading to version 3.15.0 or greater.

## References
- https://lists.debian.org/debian-lts-announce/2023/04/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3DVUZPALAQ34TQP6KFNLM4IZS6B32XSA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5PAGL5M2KGYPN3VEQCRJJE6NA7D5YG5X/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BTRGBRC5KGCA4SK5MUNLPYJRAGXMBIYY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IFX6KPNOFHYD6L4XES5PCM3QNSKZBOTQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KQJB6ZPRLKV6WCMX2PRRRQBFAOXFBK6B/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MRWRAXAFR3JR7XCFWTHC2KALSZKWACCE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NVTWVQRB5OCCTMKEQFY5MYED3DXDVSLP/
- https://github.com/protocolbuffers/protobuf/releases/tag/v3.15.0
- https://security.netapp.com/advisory/ntap-20220429-0005/
- https://www.oracle.com/security-alerts/cpuapr2022.html
