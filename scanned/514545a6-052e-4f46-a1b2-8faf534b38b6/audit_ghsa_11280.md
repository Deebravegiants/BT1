# [H] Modoboa has OS Command Injection

## Summary
Severity: High
Advisory: GHSA-wwv8-cqpr-vx3m
CVE: CVE-2026-27602
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-wwv8-cqpr-vx3m
Type: github-advisory

## Affected
- PyPI: `modoboa` — affected >=0 <2.7.1

## Details
### Summary

`exec_cmd()` in `modoboa/lib/sysutils.py` always runs subprocess calls with `shell=True`. Since domain names flow directly into shell command strings without any sanitization, a Reseller or SuperAdmin can include shell metacharacters in a domain name to run arbitrary OS commands on the server.

### Details

The root cause is in `modoboa/lib/sysutils.py:31`:

```python
kwargs["shell"] = True
process = subprocess.Popen(cmd, **kwargs)
```

When a create a domain is created with DKIM enabled, the domain name gets embedded into a shell command like this:

```python
exec_cmd(f"openssl genrsa -out {dkim_storage_dir}/{domain.name}.pem {key_size}")
```

If the domain name contains something like `$(id>/tmp/proof).example.com`, the shell executes the injected command before running openssl.

The same pattern appears in several other places:

- `modoboa/admin/jobs.py:38` — mailbox rename via `mv` using `full_address`
- `modoboa/amavis/lib.py:202` — `sa-learn` using `domain.name`
- `modoboa/admin/models/mailbox.py:150` — `doveadm user` using `full_address`
- `modoboa/maillog/graphics.py:105–107` — `rrdtool` using `domain.name`
- `modoboa/webmail/models.py:54–57` — `doveadm move/delete` using `account.email`

### PoC

1. Deploy modoboa <= 2.7.0
2. Log in as a Reseller or SuperAdmin
3. Create a new domain named `$(id>/tmp/proof).example.com` with DKIM enabled
4. SSH into the server and read `/tmp/proof`

Something like this will be displayed:

```
uid=0(root) gid=0(root) groups=0(root)
```

Confirmed on commit b521bcb4f (latest main at time of discovery).

### Impact

An attacker with Reseller-level access (or higher) can execute arbitrary OS commands on the mail server — in a typical Modoboa deployment this means running as root. All six identified sinks are reachable through normal application workflows.

## References
- https://github.com/modoboa/modoboa/security/advisories/GHSA-wwv8-cqpr-vx3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-27602
- https://github.com/modoboa/modoboa/commit/27a7aa133d3608fe8c25ae39125d1012c333cbfa
- https://github.com/modoboa/modoboa
- https://github.com/modoboa/modoboa/releases/tag/2.7.1
