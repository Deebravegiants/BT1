# [M] CVE-2020-11088

## Summary
Severity: Medium
Advisory: CVE-2020-11088
Aliases: GHSA-xh4f-fh87-43hp
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2020-05-29
Source: https://osv.dev/vulnerability/CVE-2020-11088
Type: osv

## Details
In FreeRDP less than or equal to 2.0.0, there is an out-of-bound read in ntlm_read_NegotiateMessage. This has been fixed in 2.1.0.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00080.html
- https://github.com/FreeRDP/FreeRDP/commit/8fa38359634a9910b91719818ab02f23c320dbae
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-xh4f-fh87-43hp
- https://lists.debian.org/debian-lts-announce/2023/10/msg00008.html
