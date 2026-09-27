# [H] CVE-2024-1580

## Summary
Severity: High
Advisory: CVE-2024-1580
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-19
Source: https://osv.dev/vulnerability/CVE-2024-1580
Type: osv

## Details
An integer overflow in dav1d AV1 decoder that can occur when decoding videos with large frame size. This can lead to memory corruption within the AV1 decoder. We recommend upgrading past version 1.4.0 of dav1d.

## References
- https://code.videolan.org/videolan/dav1d/-/releases/1.4.0
- https://support.apple.com/kb/HT214094
- https://support.apple.com/kb/HT214098
- https://code.videolan.org/videolan/dav1d/-/blob/master/NEWS
- https://support.apple.com/kb/HT214093
- https://support.apple.com/kb/HT214095
- https://support.apple.com/kb/HT214096
- https://support.apple.com/kb/HT214097
- http://seclists.org/fulldisclosure/2024/Mar/38
- http://seclists.org/fulldisclosure/2024/Mar/39
- http://seclists.org/fulldisclosure/2024/Mar/37
- http://seclists.org/fulldisclosure/2024/Mar/40
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/5EPMUNDMEBGESOJ2ZNCWYEAYOOEKNWOO/
- http://seclists.org/fulldisclosure/2024/Mar/36
- http://seclists.org/fulldisclosure/2024/Mar/41
