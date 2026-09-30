# [M] CVE-2018-16253

## Summary
Severity: Medium
Advisory: CVE-2018-16253
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-16253
Type: osv

## Details
In sig_verify() in x509.c in axTLS version 2.1.3 and before, the PKCS#1 v1.5 signature verification does not properly verify the ASN.1 metadata. Consequently, a remote attacker can forge signatures when small public exponents are being used, which could lead to impersonation through fake X.509 certificates. This is an even more permissive variant of CVE-2006-4790 and CVE-2014-1568.

## References
- https://github.com/igrr/axtls-8266/commit/5efe2947ab45e81d84b5f707c51d1c64be52f36c
- https://sourceforge.net/p/axtls/mailman/message/36459928/
