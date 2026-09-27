# [M] CVE-2020-8939

## Summary
Severity: Medium
Advisory: CVE-2020-8939
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-8939
Type: osv

## Details
An out of bounds read on the enc_untrusted_inet_ntop function allows an attack to extend the result size that is used by memcpy() to read memory from within the enclave heap. We recommend upgrading past commit 6ff3b77ffe110a33a2f93848a6333f33616f02c4

## References
- https://github.com/google/asylo/commit/6ff3b77ffe110a33a2f93848a6333f33616f02c4
