# [M] An authentication bypass vulnerability exists in libcurl prior to v8.0.0 where it reuses a...

## Summary
Severity: Medium
Advisory: JLSEC-2025-33
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-33
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.0.1+0

## Details
An authentication bypass vulnerability exists in libcurl prior to v8.0.0 where it reuses a previously established SSH connection despite the fact that an SSH option was modified, which should have prevented reuse. libcurl maintains a pool of previously used connections to reuse them for subsequent transfers if the configurations match. However, two SSH settings were omitted from the configuration check, allowing them to match easily, potentially leading to the reuse of an inappropriate connection.

## References
- https://hackerone.com/reports/1898475
- https://lists.debian.org/debian-lts-announce/2023/04/msg00025.html
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230420-0010/
