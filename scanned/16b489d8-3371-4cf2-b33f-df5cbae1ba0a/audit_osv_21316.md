# [H] CVE-2021-42075

## Summary
Severity: High
Advisory: CVE-2021-42075
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-08
Source: https://osv.dev/vulnerability/CVE-2021-42075
Type: osv

## Details
An issue was discovered in Barrier before 2.3.4. The barriers component (aka the server-side implementation of Barrier) does not correctly close file descriptors for established TCP connections. An unauthenticated remote attacker can thus cause file descriptor exhaustion in the server process, leading to denial of service.

## References
- https://github.com/debauchee/barrier/releases/tag/v2.3.4
- http://www.openwall.com/lists/oss-security/2021/11/02/4
