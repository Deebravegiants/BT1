# [C] CVE-2022-45132

## Summary
Severity: Critical
Advisory: CVE-2022-45132
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-18
Source: https://osv.dev/vulnerability/CVE-2022-45132
Type: osv

## Details
In Linaro Automated Validation Architecture (LAVA) before 2022.11.1, remote code execution can be achieved through user-submitted Jinja2 template. The REST API endpoint for validating device configuration files in lava-server loads input as a Jinja2 template in a way that can be used to trigger remote code execution in the LAVA server.

## References
- https://lists.lavasoftware.org/archives/list/lava-announce%40lists.lavasoftware.org/thread/WHXGQMIZAPW3GCQEXYHC32N2ZAAAIYCY/
- https://podalirius.net/en/articles/python-vulnerabilities-code-execution-in-jinja-templates/
