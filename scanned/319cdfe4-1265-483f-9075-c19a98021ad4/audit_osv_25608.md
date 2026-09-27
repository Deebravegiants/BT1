# [H] Incomplete Internal State Distinction in ntpsec

## Summary
Severity: High
Advisory: CVE-2023-4012
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-07
Source: https://osv.dev/vulnerability/CVE-2023-4012
Type: osv

## Details
ntpd will crash if the server is not NTS-enabled (no certificate) and it receives an NTS-enabled client request (mode 3).

## References
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1038422
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4012.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-4012
- https://gitlab.com/NTPsec/ntpsec/-/issues/794
