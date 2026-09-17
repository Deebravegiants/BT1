# [M] CVE-2021-22897

## Summary
Severity: Medium
Advisory: CVE-2021-22897
Aliases: CURL-CVE-2021-22897
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-06-11
Source: https://osv.dev/vulnerability/CVE-2021-22897
Type: osv

## Details
curl 7.61.0 through 7.76.1 suffers from exposure of data element to wrong session due to a mistake in the code for CURLOPT_SSL_CIPHER_LIST when libcurl is built to use the Schannel TLS library. The selected cipher set was stored in a single "static" variable in the library, which has the surprising side-effect that if an application sets up multiple concurrent transfers, the last one that sets the ciphers will accidentally control the set used by all transfers. In a worst-case scenario, this weakens transport security significantly.

## References
- https://security.netapp.com/advisory/ntap-20210727-0007/
- https://hackerone.com/reports/1172857
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://curl.se/docs/CVE-2021-22897.html
- https://github.com/curl/curl/commit/bbb71507b7bab52002f9b1e0880bed6a32834511
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujan2022.html
