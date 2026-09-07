# [H] Eval Injection in fastbots

## Summary
Severity: High
Advisory: GHSA-vccg-f4gp-45x9
CVE: CVE-2023-48699
CWE: CWE-94, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-21
Source: https://github.com/advisories/GHSA-vccg-f4gp-45x9
Type: github-advisory

## Affected
- PyPI: `fastbots` — affected >=0 <0.1.5

## Details
### Impact
An attacker could modify the locators.ini locator file with python code that without proper validation it's executed and it could lead to rce. The vulnerability is in the function def __locator__(self, locator_name: str) in page.py. The vulnerable code that load and execute directly from the file without validation it's:
```python
 return eval(self._bot.locator(self._page_name, locator_name))
```

### Patches
In order to mitigate this issue it's important to upgrade to fastbots version 0.1.5 or above. 

### References
[Merge that fix also this issue](https://github.com/ubertidavide/fastbots/pull/3#issue-2003080806)

## References
- https://github.com/ubertidavide/fastbots/security/advisories/GHSA-vccg-f4gp-45x9
- https://nvd.nist.gov/vuln/detail/CVE-2023-48699
- https://github.com/ubertidavide/fastbots/pull/3#issue-2003080806
- https://github.com/ubertidavide/fastbots/commit/73eb03bd75365e112b39877e26ef52853f5e9f57
- https://github.com/ubertidavide/fastbots
