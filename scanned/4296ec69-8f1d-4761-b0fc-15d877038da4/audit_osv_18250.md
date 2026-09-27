# [H] CVE-2020-25646

## Summary
Severity: High
Advisory: CVE-2020-25646
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-29
Source: https://osv.dev/vulnerability/CVE-2020-25646
Type: osv

## Details
A flaw was found in Ansible Collection community.crypto. openssl_privatekey_info exposes private key in logs. This directly impacts confidentiality

## References
- https://github.com/ansible-collections/community.crypto/commit/233d1afc296f6770e905a1785ee2f35af7605e43
