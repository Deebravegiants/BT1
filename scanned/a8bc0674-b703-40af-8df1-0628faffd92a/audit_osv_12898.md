# [M] CVE-2018-16149

## Summary
Severity: Medium
Advisory: CVE-2018-16149
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-07
Source: https://osv.dev/vulnerability/CVE-2018-16149
Type: osv

## Details
In sig_verify() in x509.c in axTLS version 2.1.3 and before, the PKCS#1 v1.5 signature verification blindly trusts the declared lengths in the ASN.1 structure. Consequently, when small public exponents are being used, a remote attacker can generate purposefully crafted signatures (and put them on X.509 certificates) to induce illegal memory access and crash the verifier.

## References
- https://github.com/igrr/axtls-8266/commit/5efe2947ab45e81d84b5f707c51d1c64be52f36c
- https://sourceforge.net/p/axtls/mailman/message/36459928/
