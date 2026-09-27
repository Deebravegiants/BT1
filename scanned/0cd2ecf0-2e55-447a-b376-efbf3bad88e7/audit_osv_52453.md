# [H] CVE-2021-47464

## Summary
Severity: High
Advisory: CVE-2021-47464
CVSS: 7.4 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47464
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

audit: fix possible null-pointer dereference in audit_filter_rules

Fix  possible null-pointer dereference in audit_filter_rules.

audit_filter_rules() error: we previously assumed 'ctx' could be null

## References
- https://git.kernel.org/stable/c/16802fa4c33eb1a8efb23f1e93365190e4047d05
- https://git.kernel.org/stable/c/4e9e46a700201b4c85081fd478c99c692a9aaa0d
- https://git.kernel.org/stable/c/6e3ee990c90494561921c756481d0e2125d8b895
- https://git.kernel.org/stable/c/d6f451f1f60c58d73038c7c3177066f8f084e2a2
