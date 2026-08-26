# [C] `sui-execution-cut` was removed from crates.io for malicious code

## Summary
Severity: Critical
Chain: sui-execution-cut
Component: sui-execution-cut
CWE: Embedded Malicious Code
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-qprh-m6p3-hwxc
Type: github-advisory

## Details
`sui-execution-cut` included a build script that attempted to exfiltrate data from the build machine.

The malicious crate had 1 version published on 2026-04-20 and had no evidence of actual usage. This crate had no dependencies on crates.io.
