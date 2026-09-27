# [H] CVE-2019-13984

## Summary
Severity: High
Advisory: CVE-2019-13984
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-19
Source: https://osv.dev/vulnerability/CVE-2019-13984
Type: osv

## Details
Directus 7 API before 2.3.0 does not validate uploaded files. Regardless of the file extension or MIME type, there is a direct link to each uploaded file, accessible by unauthenticated users, as demonstrated by the EICAR Anti-Virus Test File.

## References
- https://github.com/directus/api/projects/44
- https://github.com/directus/api/issues/981
