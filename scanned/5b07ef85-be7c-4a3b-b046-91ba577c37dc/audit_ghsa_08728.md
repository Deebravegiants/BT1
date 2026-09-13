# [H] Cowboy: Unbounded buffer accumulation in multipart header parsing causes denial of service in cowboy

## Summary
Severity: High
Advisory: GHSA-jfc2-q6qh-g5x8
CVE: CVE-2026-8466
CWE: CWE-770
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-jfc2-q6qh-g5x8
Type: github-advisory

## Affected
- Hex: `cowboy` — affected >=2.0.0 <2.15.0

## Details
Allocation of Resources Without Limits or Throttling vulnerability in ninenines cowboy allows denial of service via unbounded buffer accumulation in multipart header parsing.

cowboy_req:read_part/3 in src/cowboy_req.erl accumulates incoming request bytes into a Buffer binary with no upper-bound check. When cow_multipart:parse_headers/2 returns more or {more, Buffer2}, the function reads up to Length bytes (default 64 KB) from the request body and recurses with the enlarged buffer. There is no equivalent of the byte_size(Acc) > Length guard present in the sibling function read_part_body/4. An unauthenticated attacker can send a multipart/form-data request whose body never yields a complete header section — for example, a body that never contains the advertised boundary delimiter, or one whose header lines never contain \r\n\r\n — and force the server process to accumulate memory linearly with the bytes the protocol layer is willing to deliver. A handful of concurrent such uploads is sufficient to exhaust BEAM memory.

This issue affects cowboy from 2.0.0 before 2.15.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8466
- https://github.com/ninenines/cowboy/commit/5c6a2061b41bb5771c4659fac7d5a822dca5bafb
- https://cna.erlef.org/cves/CVE-2026-8466.html
- https://github.com/ninenines/cowboy
- https://osv.dev/vulnerability/EEF-CVE-2026-8466
