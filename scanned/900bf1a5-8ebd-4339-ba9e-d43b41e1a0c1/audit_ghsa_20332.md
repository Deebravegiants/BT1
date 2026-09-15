# [H] Link Following in Deno

## Summary
Severity: High
Advisory: GHSA-67hm-27mx-9cg7
CVE: CVE-2021-41641
CWE: CWE-59
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-06-13
Source: https://github.com/advisories/GHSA-67hm-27mx-9cg7
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=0 <1.16.0

## Details
Deno <=1.14.0 file sandbox does not handle symbolic links correctly. When running Deno with specific write access, the Deno.symlink method can be used to gain access to any directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41641
- https://github.com/denoland/deno/issues/12152
- https://github.com/denoland/deno/pull/12554
- https://github.com/denoland/deno/commit/d44011a69e0674acfa9c59bd7ad7f0523eb61d42
- https://hackers.report/report/614876917a7b150012836bb8
