# [H] CVE-2019-19324

## Summary
Severity: High
Advisory: CVE-2019-19324
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-03-20
Source: https://osv.dev/vulnerability/CVE-2019-19324
Type: osv

## Details
Xmidt cjwt through 1.0.1 before 2019-11-25 maps unsupported algorithms to alg=none, which sometimes leads to untrusted accidental JWT acceptance.

## References
- https://github.com/xmidt-org/cjwt/commit/9304d3e94242c1a6df77b21bde0e949392e1040a
- https://github.com/xmidt-org/cjwt/pull/29#issuecomment-558356866
