# [H] CVE-2021-3528

## Summary
Severity: High
Advisory: CVE-2021-3528
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-3528
Type: osv

## Details
A flaw was found in noobaa-operator in versions before 5.7.0, where internal RPC AuthTokens between the noobaa operator and the noobaa core are leaked into log files. An attacker with access to the log files could use this AuthToken to gain additional access into noobaa deployment and can read/modify system configuration.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1955601
