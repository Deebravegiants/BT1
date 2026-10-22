# [H] CVE-2020-36402

## Summary
Severity: High
Advisory: CVE-2020-36402
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-07-01
Source: https://osv.dev/vulnerability/CVE-2020-36402
Type: osv

## Details
Solidity 0.7.5 has a stack-use-after-return issue in smtutil::CHCSmtLib2Interface::querySolver. NOTE: c39a5e2b7a3fabbf687f53a2823fc087be6c1a7e is cited in the OSV "fixed" field but does not have a code change.

## References
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/solidity/OSV-2020-2131.yaml
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26997
- https://github.com/ethereum/solidity/commit/c39a5e2b7a3fabbf687f53a2823fc087be6c1a7e
