# [H] JupyterLab's command linker attributes in HTML enable one-click command execution from untrusted content

## Summary
Severity: High
Advisory: GHSA-mqcg-5x36-vfcg
CVE: CVE-2026-42557
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-mqcg-5x36-vfcg
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=0 <4.5.7
- PyPI: `notebook` — affected >=7.0.0 <7.5.6

## Details
JupyterLab's HTML sanitizer allowlists `data-commandlinker-command` and `data-commandlinker-args` on `button` elements, while `CommandLinker` listens for all click events on `document.body` and executes the named command without checking whether the element came from trusted JupyterLab UI. A notebook with a pre-saved HTML cell output containing a deceptive button can trigger arbitrary JupyterLab commands - including arbitrary code execution - on a single user click, without any code being submitted for execution by the user.

### Impact

An attacker who shares a notebook or a Markdown file - via email, GitHub, or a Binder link - can invoke an arbitrary command upon a single click by the victim. The button can be rendered inside the output area and be visually indistinguishable from a legitimate widget. No kernel needs to start; the HTML output is stored in the notebook file and displayed immediately on open.

#### Single-click impact

An attacker convincing the victim to click on a single button or link can:
- execute arbitrary code in the available kernels,
- delete files leading to information loss; in principle the loss could be unrecoverable, depending on server configuration and attack complexity,
- open multiple kernels/terminals at once, or create multiple files at once, putting significant stress on the server and thus deny availability for other users when using standalone multi-tenant jupyter-server deployment, and to a lesser degree impact availability on JupyterHub deployments.

The arbitrary code execution will be immediately visible to the user; and can be halted by the timely user intervention. The deletion of files can be silent and go unnoticed for some time.

#### Multi-click attacks

An attacker who convinces the victim to click on multiple buttons in specific order and to grant access to clipboard (or in scenarios where the user already granted keyboard access) can obtain full access to the terminal and execute arbitrary commands in the environment with access scope that might exceed that of available kernels. Only users of Chromium-based browsers are susceptible to this expanded variant of the attack.

The execution of commands in the terminal would be immediately visible to the user.

#### Impact of third-party extensions

The impact described above assumes a plain JupyterLab/Notebook installation. In environments with frontend extensions that contribute additional commands the attack surface is increased by the functionality covered by these commands.

### Patches

JupyterLab 4.5.7

### Workarounds

No workarounds are available for end-users.

Downstream applications inheriting from `JupyterFrontEnd` or `JupyterLab` can effectively disable the `CommandLinker` by passing `commandLinker: new CommandLinker({ commands: new CommandRegistry() })` option in the initialization options.

### Hardening

The patched versions include a toggle to disable the command linker functionality altogether, for example via `overrides.json`:

```json
{
  "@jupyterlab/apputils-extension:sanitizer": {
    "allowCommandLinker": false
  }
}
```

### Resources

- https://jupyterlab.readthedocs.io/en/latest/user/commands.html#commands-in-markdown-files

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-mqcg-5x36-vfcg
- https://nvd.nist.gov/vuln/detail/CVE-2026-42557
- https://github.com/jupyterlab/jupyterlab
- https://jupyterlab.readthedocs.io/en/latest/user/commands.html#commands-in-markdown-files
