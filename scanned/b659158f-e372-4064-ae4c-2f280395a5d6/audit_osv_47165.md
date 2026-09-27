# [H] CVE-2016-0807

## Summary
Severity: High
Advisory: CVE-2016-0807
CVSS: 8.4 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-02-07
Source: https://osv.dev/vulnerability/CVE-2016-0807
Type: osv

## Details
The get_build_id function in elf_utils.cpp in Debuggerd in Android 6.x before 2016-02-01 allows attackers to gain privileges via a crafted application that mishandles a Desc Size element in an ELF Note, aka internal bug 25187394.

## References
- https://android.googlesource.com/platform%2Fsystem%2Fcore/+/d917514bd6b270df431ea4e781a865764d406120
- http://source.android.com/security/bulletin/2016-02-01.html
