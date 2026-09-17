# [M] Headers containing newline characters can split messages in hyper

## Summary
Severity: Medium
Advisory: GHSA-q89x-f52w-6hj2
CVE: CVE-2017-18587
CWE: CWE-93
Ecosystem: crates.io
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-q89x-f52w-6hj2
Type: github-advisory

## Affected
- crates.io: `hyper` — affected >=0.10.0 <0.10.2
- crates.io: `hyper` — affected >=0 <0.9.18

## Details
Serializing of headers to the socket did not filter the values for newline bytes (\r or \n), which allowed for header values to split a request or response. People would not likely include newlines in the headers in their own applications, so the way for most people to exploit this is if an application constructs headers based on unsanitized user input.

This issue was fixed by replacing all newline characters with a space during serialization of a header value.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-18587
- https://github.com/hyperium/hyper
- https://github.com/hyperium/hyper/wiki/Security-001
- https://rustsec.org/advisories/RUSTSEC-2017-0002.html
