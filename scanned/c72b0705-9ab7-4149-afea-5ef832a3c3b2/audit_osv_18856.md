# [C] CVE-2020-36617

## Summary
Severity: Critical
Advisory: CVE-2020-36617
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2020-36617
Type: osv

## Details
A vulnerability was found in ewxrjk sftpserver. It has been declared as problematic. Affected by this vulnerability is the function sftp_parse_path of the file parse.c. The manipulation leads to uninitialized pointer. The real existence of this vulnerability is still doubted at the moment. The name of the patch is bf4032f34832ee11d79aa60a226cc018e7ec5eed. It is recommended to apply a patch to fix this issue. The identifier VDB-216205 was assigned to this vulnerability. NOTE: In some deployment models this would be a vulnerability. README specifically warns about avoiding such deployment models.

## References
- https://vuldb.com/?id.216205
- https://github.com/ewxrjk/sftpserver/commit/bf4032f34832ee11d79aa60a226cc018e7ec5eed
