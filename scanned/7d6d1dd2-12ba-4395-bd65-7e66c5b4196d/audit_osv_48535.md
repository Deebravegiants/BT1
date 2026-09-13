# [H] CVE-2017-9106

## Summary
Severity: High
Advisory: CVE-2017-9106
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-18
Source: https://osv.dev/vulnerability/CVE-2017-9106
Type: osv

## Details
An issue was discovered in adns before 1.5.2. adns_rr_info mishandles a bogus *datap. The general pattern for formatting integers is to sprintf into a fixed-size buffer. This is correct if the input is in the right range; if it isn't, the buffer may be overrun (depending on the sizes of the types on the current platform). Of course the inputs ought to be right. And there are pointers in there too, so perhaps one could say that the caller ought to check these things. It may be better to require the caller to make the pointer structure right, but to have the code here be defensive about (and tolerate with an error but without crashing) out-of-range integer values. So: it should defend each of these integer conversion sites with a check for the actual permitted range, and return adns_s_invaliddata if not. The lack of this check causes the SOA sign extension bug to be a serious security problem: the sign extended SOA value is out of range, and overruns the buffer when reconverted. This is related to sign extending SOA 32-bit integer fields, and use of a signed data type.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UGFZ4SPV6KFQK6ZNUZFB5Y32OYFOM5YJ/
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git%3Ba=blob%3Bf=changelog
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRVHN3GGVNQWAOL3PWC5FLAV7HUESLZR/
- https://www.chiark.greenend.org.uk/pipermail/adns-announce/2020/000004.html
- http://www.chiark.greenend.org.uk/ucgi/~ianmdlvl/git?p=adns.git
