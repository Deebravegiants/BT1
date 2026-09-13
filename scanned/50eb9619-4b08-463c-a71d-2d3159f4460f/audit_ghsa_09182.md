# [M] Diesel: Command injection in Diesel's implementation of `COPY FROM`/`COPY TO`

## Summary
Severity: Medium
Advisory: GHSA-m9p2-fxp5-v3fp
CWE: CWE-88
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-m9p2-fxp5-v3fp
Type: github-advisory

## Affected
- crates.io: `diesel` — affected >=0 <2.3.8

## Details
Diesel allows users to configure various options for PostgreSQL's `COPY FROM` and `COPY TO` statements. These configurations are partially provided as strings or characters. 

Diesel did not check if any these user-provided options contain a quote character `'`, which can lead to the injection of additional options in the current `COPY FROM`/`COPY TO` statement. 

This vulnerability affects any user of `COPY FROM`/`COPY TO` that passes user-provided input to any of the affected functions. It can result in modifications of options in the current statement, but it is not possible inject additional statements.

## Mitigation

The preferred mitigation to the outlined problem is to update to Diesel version 2.3.8 or newer, which includes fixes for the problem.

## Resolution

Diesel now correctly escapes any quotes contained in the provided arguments.

## References
- https://github.com/diesel-rs/diesel/pull/5042
- https://github.com/diesel-rs/diesel
- https://rustsec.org/advisories/RUSTSEC-2026-0136.html
