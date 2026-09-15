# [M] Issue summary: The AES-XTS cipher decryption implementation for 64 bit ARM platform contains a bug...

## Summary
Severity: Medium
Advisory: JLSEC-2026-238
Ecosystem: Julia
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/JLSEC-2026-238
Type: osv

## Affected
- Julia: `OpenSSL_jll` — affected >=3.0.8+0 <3.0.9+0

## Details
Issue summary: The AES-XTS cipher decryption implementation for 64 bit ARM
platform contains a bug that could cause it to read past the input buffer,
leading to a crash.

Impact summary: Applications that use the AES-XTS algorithm on the 64 bit ARM
platform can crash in rare circumstances. The AES-XTS algorithm is usually
used for disk encryption.

The AES-XTS cipher decryption implementation for 64 bit ARM platform will read
past the end of the ciphertext buffer if the ciphertext size is 4 mod 5 in 16
byte blocks, e.g. 144 bytes or 1024 bytes. If the memory after the ciphertext
buffer is unmapped, this will trigger a crash which results in a denial of
service.

If an attacker can control the size and location of the ciphertext buffer
being decrypted by an application using AES-XTS on 64 bit ARM, the
application is affected. This is fairly unlikely making this issue
a Low severity one.

## References
- http://www.openwall.com/lists/oss-security/2023/04/20/13
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=02ac9c9420275868472f33b01def01218742b8bb
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=bc2f61ad70971869b242fc1cb445b98bad50074a
- https://github.com/advisories/GHSA-4wp2-xw7p-2gfx
- https://nvd.nist.gov/vuln/detail/CVE-2023-1255
- https://security.netapp.com/advisory/ntap-20230908-0006/
- https://www.openssl.org/news/secadv/20230419.txt
