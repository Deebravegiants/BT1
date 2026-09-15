# [C] CVE-2018-11574

## Summary
Severity: Critical
Advisory: CVE-2018-11574
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-14
Source: https://osv.dev/vulnerability/CVE-2018-11574
Type: osv

## Details
Improper input validation together with an integer overflow in the EAP-TLS protocol implementation in PPPD may cause a crash, information disclosure, or authentication bypass. This implementation is distributed as a patch for PPPD 0.91, and includes the affected eap.c and eap-tls.c files. Configurations that use the `refuse-app` option are unaffected.

## References
- https://usn.ubuntu.com/3810-1/
- http://www.openwall.com/lists/oss-security/2018/06/11/1
