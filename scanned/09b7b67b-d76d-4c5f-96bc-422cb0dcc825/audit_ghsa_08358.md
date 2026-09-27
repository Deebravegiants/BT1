# [H] compliance-trestle - jinja has an Arbitrary File Write via Path Traversal

## Summary
Severity: High
Advisory: GHSA-4q5v-7g7x-j79w
CVE: CVE-2026-46345
CWE: CWE-22, CWE-36, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-28
Source: https://github.com/advisories/GHSA-4q5v-7g7x-j79w
Type: github-advisory

## Affected
- PyPI: `compliance-trestle` — affected >=4.0.0 <4.0.3
- PyPI: `compliance-trestle` — affected >=0 <3.12.2

## Details
**Relevant Products/Components:**

* `trestle/core/commands/author/jinja.py`
* `trestle author jinja`

---

## Detailed Description:

The `-o/--output` argument in `trestle author jinja` allows writing files outside the intended workspace.

The application does not properly validate:

* `../`
* `..\`
* absolute paths

This allows arbitrary file write to attacker-controlled locations.

Vulnerable code:

```python
output_file = trestle_root / r_output_file
```

An attacker can overwrite files such as:

* `.github/workflows/*.yml`
* `.git/hooks/*`
* user writable config files

This can lead to CI/CD compromise or local code execution.

---

## Steps To Reproduce:

1. Clone the repository:

```bash
git clone https://github.com/oscal-compass/compliance-trestle.git
cd compliance-trestle
```

2. Create template:

```bash
echo "hello" > template.j2
```

3. Run:

```powershell
trestle author jinja -i template.j2 -o "subdir\..\..\..\..\..\poc.txt"
```

4. Observe:

```powershell
dir E:\poc.txt
```

The file is written outside the repository workspace.

---

## Browsers Verified In:

Not browser related.

Tested on:

* Windows 11
* Python 3.13

---

## Supporting Material/References:

Affected file:

```text
trestle/core/commands/author/jinja.py
```

Successfully verified:

* directory traversal using `../`
* Windows traversal using `..\`
* arbitrary file write outside workspace

---

## Access Vector Required for Exploitation:

Local

---

## Vulnerability Exists in Default Configuration?:

Yes

---

## Is the exploitation trivial or does it involve a multi-step process that may depend on user/victim interaction?:

Trivial.
Single command execution.

---

## Exploitation Requires Authentication?:

No

---

## Under what privileges does the vulnerable service or component run?:

Runs with privileges of the user executing the `trestle` command.

## Impact

An attacker can write files outside the intended workspace directory and overwrite sensitive files writable by the current user.

Possible impacts include:

* overwriting `.github/workflows/*.yml` to execute attacker-controlled GitHub Actions workflows
* overwriting `.git/hooks/*` for local code execution
* modifying user configuration files such as `.bashrc`
* tampering with repository files and generated compliance artifacts

In CI/CD environments, this may result in execution of attacker-controlled commands on build runners.

## References
- https://github.com/oscal-compass/compliance-trestle/security/advisories/GHSA-4q5v-7g7x-j79w
- https://nvd.nist.gov/vuln/detail/CVE-2026-46345
- https://github.com/oscal-compass/compliance-trestle/commit/247fcce289f60103f3d8e28d8ec51a6986b94fb6
- https://github.com/oscal-compass/compliance-trestle/commit/7d107b3ac53caca7bde97a6278b23cd739d94525
- https://github.com/oscal-compass/compliance-trestle
- https://github.com/pypa/advisory-database/tree/main/vulns/compliance-trestle/PYSEC-2026-2423.yaml
