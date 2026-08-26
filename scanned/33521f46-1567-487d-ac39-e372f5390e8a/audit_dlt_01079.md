# [M] Stack overflow when parsing specially crafted JSON ABI strings

## Summary
Severity: Medium
Chain: alloy-json-abi
Component: alloy-json-abi
CWE: Uncontrolled Resource Consumption
Published: 2024-08-15
Source: https://github.com/advisories/GHSA-8327-84cj-8xjm
Type: github-advisory

## Details
Affected versions of the `alloy-json-abi` crate did not properly handle parsing of malformatted JSON ABI strings. The `JsonAbi::parse` method can be tricked into a stack overflow when processing specially crafted input. 

This stack overflow can lead to a crash of the application using this crate, potentially causing a denial of service.

The flaw was corrected in commit [4790c47](https://github.com/alloy-rs/core/commit/4790c47518024bd391bbd6815b00f501bad76a15).
