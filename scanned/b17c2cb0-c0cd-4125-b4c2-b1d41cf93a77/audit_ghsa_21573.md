# [H] MessagePack for Golang subject to DoS via Unmarshal panic

## Summary
Severity: High
Advisory: GHSA-jr77-8gx4-h5qh
CVE: CVE-2022-41719
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-11
Source: https://github.com/advisories/GHSA-jr77-8gx4-h5qh
Type: github-advisory

## Affected
- Go: `github.com/shamaton/msgpack/v2` — affected >=0 <2.1.1

## Details
Unmarshal can panic on some inputs, possibly allowing for denial of service attacks. This issue has been patched in version 2.1.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41719
- https://github.com/shamaton/msgpack/issues/31
- https://github.com/shamaton/msgpack/pull/32
- https://github.com/shamaton/msgpack
- https://github.com/shamaton/msgpack/releases/tag/v2.1.1
- https://pkg.go.dev/vuln/GO-2022-0972
