# [C] SM2 Decryption Buffer Overflow

## Summary
Severity: Critical
Advisory: GHSA-5ww6-px42-wc85
CVE: CVE-2021-3711
CWE: CWE-120
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5ww6-px42-wc85
Type: github-advisory

## Affected
- crates.io: `openssl-src` — affected >=0 <111.16.0

## Details
In order to decrypt SM2 encrypted data an application is expected to call the API function EVP_PKEY_decrypt(). Typically an application will call this function twice. The first time, on entry, the "out" parameter can be NULL and, on exit, the "outlen" parameter is populated with the buffer size required to hold the decrypted plaintext. The application can then allocate a sufficiently sized buffer and call EVP_PKEY_decrypt() again, but this time passing a non-NULL value for the "out" parameter. A bug in the implementation of the SM2 decryption code means that the calculation of the buffer size required to hold the plaintext returned by the first call to EVP_PKEY_decrypt() can be smaller than the actual size required by the second call. This can lead to a buffer overflow when EVP_PKEY_decrypt() is called by the application a second time with a buffer that is too small. A malicious attacker who is able present SM2 content for decryption to an application could cause attacker chosen data to overflow the buffer by up to a maximum of 62 bytes altering the contents of other data held after the buffer, possibly changing application behaviour or causing the application to crash. The location of the buffer is application dependent but is typically heap allocated. Fixed in OpenSSL 1.1.1l (Affected 1.1.1-1.1.1k).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3711
- https://www.tenable.com/security/tns-2022-02
- https://www.tenable.com/security/tns-2021-16
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.openssl.org/news/secadv/20210824.txt
- https://www.debian.org/security/2021/dsa-4963
- https://security.netapp.com/advisory/ntap-20240621-0006
- https://security.netapp.com/advisory/ntap-20211022-0003
- https://security.netapp.com/advisory/ntap-20210827-0010
- https://security.gentoo.org/glsa/202210-02
- https://security.gentoo.org/glsa/202209-02
- https://rustsec.org/advisories/RUSTSEC-2021-0097.html
- https://lists.apache.org/thread.html/rad5d9f83f0d11fb3f8bb148d179b8a9ad7c6a17f18d70e5805a713d1@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/rad5d9f83f0d11fb3f8bb148d179b8a9ad7c6a17f18d70e5805a713d1%40%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r18995de860f0e63635f3008fd2a6aca82394249476d21691e7c59c9e@%3Cdev.tomcat.apache.org%3E
- https://lists.apache.org/thread.html/r18995de860f0e63635f3008fd2a6aca82394249476d21691e7c59c9e%40%3Cdev.tomcat.apache.org%3E
- https://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=59f5e75f3bced8fc0e130d72a3f582cf7b480b46
- https://git.openssl.org/gitweb/?p=openssl.git%3Ba=commitdiff%3Bh=59f5e75f3bced8fc0e130d72a3f582cf7b480b46
