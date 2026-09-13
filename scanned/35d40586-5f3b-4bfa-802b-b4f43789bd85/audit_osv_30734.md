# [C] CVE-2024-55884

## Summary
Severity: Critical
Advisory: CVE-2024-55884
CVSS: 9.0 (CVSS:3.1/AC:H/AV:N/A:H/C:H/I:H/PR:N/S:C/UI:N)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-55884
Type: osv

## Details
In the Mullvad VPN client 2024.6 (Desktop), 2024.8 (iOS), and 2024.8-beta1 (Android), the exception-handling alternate stack can be exhausted, leading to heap-based out-of-bounds writes in enable() in exception_logging/unix.rs, aka MLLVD-CR-24-01. NOTE: achieving code execution is considered non-trivial.

## References
- https://news.ycombinator.com/item?id=42390768
- https://x41-dsec.de/news/2024/12/11/mullvad/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55884.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-55884
- https://github.com/mullvad/mullvadvpn-app/commit/ef6c862071b26023802b00d6e1dc6ca53d1ab3e6
