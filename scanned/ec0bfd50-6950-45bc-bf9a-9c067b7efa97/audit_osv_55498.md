# [M] CVE-2025-58190

## Summary
Severity: Medium
Advisory: CVE-2025-58190
Aliases: GO-2026-4441
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-02-05
Source: https://osv.dev/vulnerability/CVE-2025-58190
Type: osv

## Details
The html.Parse function in golang.org/x/net/html has an infinite parsing loop when processing certain inputs, which can lead to denial of service (DoS) if an attacker provides specially crafted HTML content.

## References
- https://groups.google.com/g/golang-announce/c/jnQcOYpiR2c
- https://pkg.go.dev/vuln/GO-2026-4441
- https://github.com/golang/vulndb/issues/4441
- https://go.dev/cl/709875
