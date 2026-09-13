# [H] CVE-2018-1000070

## Summary
Severity: High
Advisory: CVE-2018-1000070
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000070
Type: osv

## Details
Bitmessage PyBitmessage version v0.6.2 (and introduced in or after commit 8ce72d8d2d25973b7064b1cf76a6b0b3d62f0ba0) contains a Eval injection vulnerability in main program, file src/messagetypes/__init__.py function constructObject that can result in Code Execution. This attack appears to be exploitable via remote attacker using a malformed message which must be processed by the victim - e.g. arrive from any sender on bitmessage network. This vulnerability appears to have been fixed in v0.6.3.

## References
- https://github.com/Bitmessage/PyBitmessage/commit/3a8016d31f517775d226aa8b902480f4a3a148a9#comments
