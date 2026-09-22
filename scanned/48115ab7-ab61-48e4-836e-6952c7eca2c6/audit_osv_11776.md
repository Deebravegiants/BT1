# [H] CVE-2017-9732

## Summary
Severity: High
Advisory: CVE-2017-9732
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2017-9732
Type: osv

## Details
The read_packet function in knc (Kerberised NetCat) before 1.11-1 is vulnerable to denial of service (memory exhaustion) that can be exploited remotely without authentication, possibly affecting another services running on the targeted host.

## References
- http://packetstormsecurity.com/files/150534/knc-Kerberized-NetCat-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2018/Nov/65
- https://github.com/elric1/knc/commit/f237f3e09ecbaf59c897f5046538a7b1a3fa40c1
- https://github.com/irsl/knc-memory-exhaustion/
