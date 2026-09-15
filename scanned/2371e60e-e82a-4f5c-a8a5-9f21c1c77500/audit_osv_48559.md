# [C] CVE-2017-9430

## Summary
Severity: Critical
Advisory: CVE-2017-9430
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9430
Type: osv

## Details
Stack-based buffer overflow in dnstracer through 1.9 allows attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a command line with a long name argument that is mishandled in a strcpy call for argv[0]. An example threat model is a web application that launches dnstracer with an untrusted name string.

## References
- https://www.exploit-db.com/exploits/42424/
- https://cxsecurity.com/issue/WLB-2017060030
- https://packetstormsecurity.com/files/142799/DNSTracer-1.8.1-Buffer-Overflow.html
- https://www.exploit-db.com/exploits/42115/
