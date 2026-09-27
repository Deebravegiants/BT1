# [C] A vulnerability was found in the Libksba library due to an integer overflow within the CRL parser

## Summary
Severity: Critical
Advisory: JLSEC-2025-93
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-17
Source: https://osv.dev/vulnerability/JLSEC-2025-93
Type: osv

## Affected
- Julia: `GnuPG_jll` — affected >=0 <2.4.7+0
- Julia: `Libksba_jll` — affected >=0 <1.6.7+0

## Details
A vulnerability was found in the Libksba library due to an integer overflow within the CRL parser. The vulnerability can be exploited remotely for code execution on the target system by passing specially crafted data to the application, for example, a malicious S/MIME attachment.

## References
- https://access.redhat.com/security/cve/CVE-2022-3515
- https://bugzilla.redhat.com/show_bug.cgi?id=2135610
- https://dev.gnupg.org/rK4b7d9cd4a018898d7714ce06f3faf2626c14582b
- https://security.netapp.com/advisory/ntap-20230706-0008/
- https://www.gnupg.org/blog/20221017-pepe-left-the-ksba.html
