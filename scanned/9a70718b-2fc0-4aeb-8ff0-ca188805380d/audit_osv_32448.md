# [H] KEX init error results with excessive memory usage

## Summary
Severity: High
Advisory: CVE-2025-30211
Aliases: GHSA-vvr3-fjhh-cfwc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-28
Source: https://osv.dev/vulnerability/CVE-2025-30211
Type: osv

## Details
Erlang/OTP is a set of libraries for the Erlang programming language. Prior to versions OTP-27.3.1, 26.2.5.10, and 25.3.2.19, a maliciously formed KEX init message can result with high memory usage. Implementation does not verify RFC specified limits on algorithm names (64 characters) provided in KEX init message. Big KEX init packet may lead to inefficient processing of the error data. As a result, large amount of memory will be allocated for processing malicious data. Versions OTP-27.3.1, OTP-26.2.5.10, and OTP-25.3.2.19 fix the issue. Some workarounds are available. One may set option `parallel_login` to `false` and/or reduce the `max_sessions` option.

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30211.json
- https://github.com/erlang/otp/security/advisories/GHSA-vvr3-fjhh-cfwc
- https://nvd.nist.gov/vuln/detail/CVE-2025-30211
