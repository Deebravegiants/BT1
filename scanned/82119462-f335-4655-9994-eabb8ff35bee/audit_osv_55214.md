# [C] CVE-2025-14308

## Summary
Severity: Critical
Advisory: CVE-2025-14308
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-14308
Type: osv

## Details
An integer overflow vulnerability exists in the write method of the Buffer class in Robocode version 1.9.3.6. The method fails to properly validate the length of data being written, allowing attackers to cause an overflow, potentially leading to buffer overflows and arbitrary code execution. This vulnerability can be exploited by submitting specially crafted inputs that manipulate the data length, leading to potential unauthorized code execution.

## References
- https://github.com/robo-code/robocode/pull/70
