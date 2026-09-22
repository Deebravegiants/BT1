# [H] CVE-2021-44657

## Summary
Severity: High
Advisory: CVE-2021-44657
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-15
Source: https://osv.dev/vulnerability/CVE-2021-44657
Type: osv

## Details
In StackStorm versions prior to 3.6.0, the jinja interpreter was not run in sandbox mode and thus allows execution of unsafe system commands. Jinja does not enable sandboxed mode by default due to backwards compatibility. Stackstorm now sets sandboxed mode for jinja by default.

## References
- https://stackstorm.com/2021/12/16/stackstorm-v3-6-0-released/
- https://github.com/pallets/jinja/issues/549
- https://github.com/StackStorm/st2/pull/5359
- https://podalirius.net/en/articles/python-vulnerabilities-code-execution-in-jinja-templates/
