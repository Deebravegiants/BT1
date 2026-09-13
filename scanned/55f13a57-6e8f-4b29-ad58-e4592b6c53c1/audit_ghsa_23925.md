# [C] curl FTP path confusion leads to NIL byte out of bounds write

## Summary
Severity: Critical
Advisory: GHSA-674j-7m97-j2p9
CVE: CVE-2018-1000120
CWE: CWE-787
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-674j-7m97-j2p9
Type: github-advisory

## Affected
- NuGet: `curl` — affected >=7.12.3

## Details
curl can be coerced into writing a zero byte out of bounds.

This bug can trigger when curl is told to work on an FTP URL, with the setting to only issue a single CWD command (--ftp-method singlecwd or the libcurl alternative [CURLOPT_FTP_FILEMETHOD](https://curl.se/libcurl/c/CURLOPT_FTP_FILEMETHOD.html)).

curl then URL-decodes the given path, calls strlen() on the result and deducts the length of the file name part to find the end of the directory within the buffer. It then writes a zero byte on that index, in a buffer allocated on the heap.

If the directory part of the URL contains a `%00` sequence, the directory length might end up shorter than the file name path, making the calculation `size_t index = directory_len - filepart_len` end up with a huge index variable for where the zero byte gets stored: `heap_buffer[index] = 0`. On several architectures that huge index will wrap and work as a negative value, thus overwriting memory before the intended heap buffer.

By using different file part lengths and putting the string `%00` in different places in the URL, an attacker that can control what paths a curl-using application uses can write that zero byte on different indexes.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000120
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://www.oracle.com/technetwork/security-advisory/cpujul2019-5072835.html
- https://www.oracle.com/technetwork/security-advisory/cpujan2019-5072801.html
- https://www.debian.org/security/2018/dsa-4136
- https://web.archive.org/web/20201220134609/http://www.securityfocus.com/bid/103414
- https://web.archive.org/web/20201220134105/http://www.securitytracker.com/id/1040531
- https://usn.ubuntu.com/3598-2
- https://usn.ubuntu.com/3598-1
- https://lists.debian.org/debian-lts-announce/2018/03/msg00012.html
- https://github.com/coapp-packages/curl
- https://curl.se/docs/CVE-2018-1000120.html
- https://curl.haxx.se/docs/adv_2018-9cd6.html
- https://access.redhat.com/errata/RHSA-2020:0594
- https://access.redhat.com/errata/RHSA-2020:0544
- https://access.redhat.com/errata/RHSA-2019:1543
- https://access.redhat.com/errata/RHSA-2018:3558
- https://access.redhat.com/errata/RHSA-2018:3157
- https://access.redhat.com/errata/RHBA-2019:0327
- http://www.oracle.com/technetwork/security-advisory/cpujul2018-4258247.html
