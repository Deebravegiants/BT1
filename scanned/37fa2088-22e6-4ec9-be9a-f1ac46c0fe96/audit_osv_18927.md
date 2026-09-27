# [H] CVE-2020-5204

## Summary
Severity: High
Advisory: CVE-2020-5204
Aliases: GHSA-wrpr-xw7q-9wvq
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-06
Source: https://osv.dev/vulnerability/CVE-2020-5204
Type: osv

## Details
In uftpd before 2.11, there is a buffer overflow vulnerability in handle_PORT in ftpcmd.c that is caused by a buffer that is 16 bytes large being filled via sprintf() with user input based on the format specifier string %d.%d.%d.%d. The 16 byte size is correct for valid IPv4 addresses (len(&#39;255.255.255.255&#39;) == 16), but the format specifier %d allows more than 3 digits. This has been fixed in version 2.11

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00034.html
- https://github.com/troglobit/uftpd/security/advisories/GHSA-wrpr-xw7q-9wvq
- https://github.com/troglobit/uftpd/commit/0fb2c031ce0ace07cc19cd2cb2143c4b5a63c9dd
