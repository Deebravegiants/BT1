# [M] CVE-2024-2466: TLS certificate check bypass with mbedTLS

## Summary
Severity: Medium (CVSS 5.3)
Program: curl
Weakness: Improper Validation of Certificate with Host Mismatch
Reporter: frankyueh
State: resolved
Disclosed: 2024-03-27T10:44:42.575Z
CVE: CVE-2016-3739, CVE-2013-4545, CVE-2013-6422, CVE-2014-0139, CVE-2014-1263, CVE-2014-2522, CVE-2014-8151, CVE-2024-2466
Source: https://hackerone.com/reports/2416725

## Details
## Summary:

Curl library has a security vulnerability where the certificate name check is bypassed when connecting to a host via its IP address. This could potentially introduce spoofing attacks or unauthorized access due to unverified server certificate.

This issue only affects the Curl with MbedTLS.

- Affected versions: from libcurl 8.5.0 to and including 8.6.0 (current master versions at the time of writing)
- Not affected versions: libcurl 8.4.0 and earlier

This issue affect all kinds of protocol over TLS session, e.g. HTTPS, FTPS, SMTPS, etc.

## Steps To Reproduce:

### (Preparation) Download and build the Curl with MbedTLS:

*Skip this step if you already have the Curl (>= 8.5.0) with MbedTLS.*

Before building the code, make sure you have environment to build the code in Linux, `sudo apt install build-essential`.

1. Get and extract the code:

```shell
wget https://curl.se/download/curl-8.6.0.tar.gz -O curl-8.6.0.tar.gz
wget https://github.com/Mbed-TLS/mbedtls/archive/refs/tags/v2.28.7.tar.gz -O mbedtls-2.28.7.tar.gz
tar zxf curl-8.6.0.tar.gz
tar zxf mbedtls-2.28.7.tar.gz
```

2. Build MbedTLS:

```shell
cd mbedtls-2.28.7
make SHARED=1 -j$(nproc)
sudo make install DESTDIR=/usr/local/lib
```

3. Build Curl with MbedTLS:


_Trimmed to 38 lines — full report: https://hackerone.com/reports/2416725_
