# [C] Flowintel Alert Settings Configuration Allows Remote Code Execution via Arbitrary Configuration Keys

## Summary
Severity: Critical
Advisory: CVE-2026-81662
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81662
Type: osv

## Details
Affected versions of Flowintel improperly trust configuration keys supplied to the alerts settings update endpoint. While configuration values were normalized to Python literals, the corresponding keys were used directly when constructing and replacing lines in conf/config_module.py.


The vulnerable code used requester-controlled keys in both the regular expression and the generated assignment:


f'{key} = {py_val}'

and appended an assignment if the key was not already present. The modified Python configuration module was subsequently reloaded using importlib.reload(). This creates a code-generation boundary in which specially crafted configuration keys can alter the Python source structure and result in execution of attacker-controlled Python statements. 

Version impacted >=3.3.0

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81662.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81662
- https://github.com/flowintel/flowintel/commit/d36171e22aed99055539260bec75e6355ada7d0c
- https://github.com/flowintel/flowintel
