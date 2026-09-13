# [H] CVE-2020-9861

## Summary
Severity: High
Advisory: CVE-2020-9861
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-11-02
Source: https://osv.dev/vulnerability/CVE-2020-9861
Type: osv

## Details
A stack overflow issue existed in Swift for Linux. The issue was addressed with improved input validation for dealing with deeply nested malicious JSON input.

## References
- https://forums.swift.org/t/swift-5-1-5-for-linux-jsonserialization-limit-recursion-when-parsing/34514
