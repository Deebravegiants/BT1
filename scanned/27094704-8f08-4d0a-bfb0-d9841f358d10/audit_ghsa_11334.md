# [H] Intake has a Command Injection via shell() Expansion in Parameter Defaults

## Summary
Severity: High
Advisory: GHSA-37g4-qqqv-7m99
CVE: CVE-2026-33310
CWE: CWE-78, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-37g4-qqqv-7m99
Type: github-advisory

## Affected
- PyPI: `intake` — affected >=0

## Details
### Summary
The shell() syntax within parameter default values appears to be automatically expanded during the catalog parsing process.
If a catalog contains a parameter default such as shell(<command>), the command may be executed when the catalog source is accessed.
This means that if a user loads a malicious catalog YAML, embedded commands could execute on the host system.
This behavior could potentially be classified as OS Command Injection / Unsafe Shell Expansion.

### Details
The issue appears to originate from how parameter default values are expanded when a catalog source is accessed.

During catalog loading and source access:

Intake resolves parameter default values
The function responsible for expanding defaults processes the shell() syntax
The shell expression triggers a subprocess execution
Because this occurs during catalog evaluation, the command may execute before the user explicitly interacts with the dataset itself.

Affected logic appears to involve:
```
expand_defaults()
```
and related parameter parsing mechanisms.


### PoC
exploit.yaml
```
metadata:
  version: 1
sources:
  rce_test:
    driver: csv
    description: "Testing shell expansion in parameters"
    args:
      urlpath: "{{ cmd_exec }}"
    parameters:
      cmd_exec:
        display_name: "Test Parameter"
        type: str
        default: "shell(touch /tmp/intake_rce_test)"
```

reproduce.py
```
import intake
import os

PROOF_FILE = "/tmp/intake_rce_test"

if os.path.exists(PROOF_FILE):
    os.remove(PROOF_FILE)

print(f"[*] Proof file exists before: {os.path.exists(PROOF_FILE)}")

try:
    cat = intake.open_catalog("exploit.yaml")

    print("Accessing source...")
    _ = cat["rce_test"]

except Exception as e:
    print(f" Error during execution: {e}")

if os.path.exists(PROOF_FILE):
    print(f" Command execution confirmed, Found: {PROOF_FILE}")
else:
    print("Command execution did not occur.")
```
### Attack Scenario
A potential attack scenario could be:

1. An attacker publishes a malicious Intake catalog YAML file
2. The victim downloads or loads the catalog
3. The victim accesses a source entry in the catalog
4. Parameter defaults are expanded
5. The shell() expression triggers execution of the embedded command

### Impact

If this behavior is confirmed to be unintended, an attacker could distribute a malicious catalog file via:

- Git repositories
- shared datasets
- URLs
- data science workflows
- Any user loading the catalog could unknowingly execute commands with their local user privileges.

### Recommendation
Possible mitigations could include:

- disabling shell() expansion by default
- requiring an explicit opt-in flag (e.g., allow_shell=True)
- restricting shell execution for catalogs loaded from untrusted sources
Please let me know if additional information or testing is needed.
I'm happy to assist with further analysis or validation.

## References
- https://github.com/intake/intake/security/advisories/GHSA-37g4-qqqv-7m99
- https://nvd.nist.gov/vuln/detail/CVE-2026-33310
- https://github.com/intake/intake/commit/d0c0b6b57c1cb3f73880655ded4a9b0e18e1fd1b
- https://github.com/intake/intake
