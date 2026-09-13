# [H] CVE-2020-13432

## Summary
Severity: High
Advisory: CVE-2020-13432
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/CVE-2020-13432
Type: osv

## Details
rejetto HFS (aka HTTP File Server) v2.3m Build #300, when virtual files or folders are used, allows remote attackers to trigger an invalid-pointer write access violation via concurrent HTTP requests with a long URI or long HTTP headers.

## References
- http://seclists.org/fulldisclosure/2021/Apr/12
- https://www.rejetto.com/hfs/?f=wn
- https://github.com/rejetto/hfs2/commit/b8ebfc4e22948e1a61506cd66e397b61ea5ea5de
- http://hyp3rlinx.altervista.org/advisories/HFS-HTTP-FILE-SERVER-v2.3-REMOTE-BUFFER-OVERFLOW-DoS.txt
- http://packetstormsecurity.com/files/157980/HFS-Http-File-Server-2.3m-Build-300-Buffer-Overflow.html
- http://seclists.org/fulldisclosure/2020/Jun/13
- https://packetstormsecurity.com/files/157980/HFS-Http-File-Server-2.3m-Build-300-Buffer-Overflow.html
