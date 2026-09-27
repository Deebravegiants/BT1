# [C] CVE-2020-14343

## Summary
Severity: Critical
Advisory: CVE-2020-14343
Aliases: GHSA-8q59-q68h-6hv4, PYSEC-2021-142
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-02-09
Source: https://osv.dev/vulnerability/CVE-2020-14343
Type: osv

## Details
A vulnerability was discovered in the PyYAML library in versions before 5.4, where it is susceptible to arbitrary code execution when it processes untrusted YAML files through the full_load method or with the FullLoader loader. Applications that use the library to process untrusted input may be vulnerable to this flaw. This flaw allows an attacker to execute arbitrary code on the system by abusing the python/object/new constructor. This flaw is due to an incomplete fix for CVE-2020-1747.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1860466
- https://github.com/SeldonIO/seldon-core/issues/2252
- https://github.com/yaml/pyyaml/issues/420
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
