# [H] CVE-2021-34797

## Summary
Severity: High
Advisory: CVE-2021-34797
Aliases: GHSA-mw25-f5r2-hpc6
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-01-04
Source: https://osv.dev/vulnerability/CVE-2021-34797
Type: osv

## Details
Apache Geode versions up to 1.12.4 and 1.13.4 are vulnerable to a log file redaction of sensitive information flaw when using values that begin with characters other than letters or numbers for passwords and security properties with the prefix "sysprop-", "javax.net.ssl", or "security-". This issue is fixed by overhauling the log file redaction in Apache Geode versions 1.12.5, 1.13.5, and 1.14.0.

## References
- https://lists.apache.org/thread/nq2w9gjzm1cjx1rh6zw41ty39qw7qpx4
- https://lists.apache.org/thread/p4l0g49rzzzpn8yt9q9p0xp52h3zmsmk
