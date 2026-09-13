# [C] CVE-2019-12929

## Summary
Severity: Critical
Advisory: CVE-2019-12929
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-24
Source: https://osv.dev/vulnerability/CVE-2019-12929
Type: osv

## Details
The QMP guest_exec command in QEMU 4.0.0 and earlier is prone to OS command injection, which allows the attacker to achieve code execution, denial of service, or information disclosure by sending a crafted QMP command to the listening server. Note: This has been disputed as a non-issue since QEMU's -qmp interface is meant to be used by trusted users. If one is able to access this interface via a tcp socket open to the internet, then it is an insecure configuration issue

## References
- https://fakhrizulkifli.github.io/posts/2019/06/06/CVE-2019-12929/
