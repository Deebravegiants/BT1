# [M] Heap buffer overflow in urbdrc channel

## Summary
Severity: Medium
Advisory: CVE-2022-39320
Aliases: GHSA-qfq2-82qr-7f4j
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-11-16
Source: https://osv.dev/vulnerability/CVE-2022-39320
Type: osv

## Details
FreeRDP is a free remote desktop protocol library and clients. Affected versions of FreeRDP may attempt integer addition on too narrow types leads to allocation of a buffer too small holding the data written. A malicious server can trick a FreeRDP based client to read out of bound data and send it back to the server. This issue has been addressed in version 2.9.0 and all users are advised to upgrade. Users unable to upgrade should not use the `/usb` redirection switch.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00034.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39320.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-qfq2-82qr-7f4j
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDOTAOJBCZKREZJPT6VZ25GESI5T6RBG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGQN3OWQNHSMWKOF4D35PF5ASKNLC74B/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39320
- https://security.gentoo.org/glsa/202401-16
