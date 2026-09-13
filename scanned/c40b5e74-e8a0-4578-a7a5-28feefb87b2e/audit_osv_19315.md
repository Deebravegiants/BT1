# [H] CVE-2021-20179

## Summary
Severity: High
Advisory: CVE-2021-20179
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-03-15
Source: https://osv.dev/vulnerability/CVE-2021-20179
Type: osv

## Details
A flaw was found in pki-core. An attacker who has successfully compromised a key could use this flaw to renew the corresponding certificate over and over again, as long as it is not explicitly revoked. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DDOLFOLEIV7I4EUC3SCZBXL6E2ER7ZEN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HRE44N6P24AEDKRMWK7RPRLMCUUBRJII/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/R3I7BRAHLE2WWSY76W3CKFCF5WSSAE24/
- https://bugzilla.redhat.com/show_bug.cgi?id=1914379
- https://github.com/dogtagpki/pki/pull/3474
- https://github.com/dogtagpki/pki/pull/3475
- https://github.com/dogtagpki/pki/pull/3476
- https://github.com/dogtagpki/pki/pull/3477
- https://github.com/dogtagpki/pki/pull/3478
