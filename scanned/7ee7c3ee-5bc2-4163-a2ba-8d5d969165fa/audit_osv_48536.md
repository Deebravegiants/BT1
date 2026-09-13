# [H] CVE-2017-9107

## Summary
Severity: High
Advisory: CVE-2017-9107
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2017-9107
Type: osv

## Details
An issue was discovered in adns before 1.5.2. It overruns reading a buffer if a domain ends with backslash. If the query domain ended with \, and adns_qf_quoteok_query was specified, qdparselabel would read additional bytes from the buffer and try to treat them as the escape sequence. It would depart the input buffer and start processing many bytes of arbitrary heap data as if it were the query domain. Eventually it would run out of input or find some other kind of error, and declare the query domain invalid. But before then it might outrun available memory and crash. In principle this could be a denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UGFZ4SPV6KFQK6ZNUZFB5Y32OYFOM5YJ/
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git%3Ba=blob%3Bf=changelog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRVHN3GGVNQWAOL3PWC5FLAV7HUESLZR/
- https://www.chiark.greenend.org.uk/pipermail/adns-announce/2020/000004.html
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git
