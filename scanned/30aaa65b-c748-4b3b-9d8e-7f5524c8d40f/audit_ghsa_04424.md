# [H] jupyterlab-git extension: Stored XSS leading to RCE

## Summary
Severity: High
Advisory: GHSA-f962-v9hr-pfg5
CVE: CVE-2026-54527
CWE: CWE-79
Ecosystem: PyPI, npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-f962-v9hr-pfg5
Type: github-advisory

## Affected
- PyPI: `jupyterlab-git` — affected >=0.30.0b3 <0.54.0
- PyPI: `jupyterlab-git-core` — affected >=0.30.0b3 <0.54.0
- npm: `@jupyterlab/git` — affected >=0.30.0b3 <0.54.0

## Details
Overview

Amazon Web Services (AWS) Security has identified a stored cross-site scripting (XSS) issue in the jupyterlab-git JupyterLab extension that can lead to remote code execution (RCE). The issue exists in the PlainTextDiff.ts component, where the createHeader() method passes Git filenames directly to innerHTML without sanitization when rendering diffs for renamed files in commit history. This allows an adversary to craft a filename containing arbitrary HTML/JavaScript that executes when another user views the rename diff in the Git History tab.

The issue can be leveraged through the rename history view in the JupyterLab Git panel. An adversary creates a file with a crafted filename containing a JavaScript payload (e.g., <img src=x onerror=eval(atob("base64_payload"))>.py), renames the file in a subsequent commit, and pushes to a shared repository. When a victim clones the repository, navigates to the Git History tab, clicks the rename commit, and then clicks the renamed file to view the diff, the unsanitized filename renders via innerHTML, executing arbitrary JavaScript in the victim's browser session. The injected JavaScript reads the xsrf cookie, opens a JupyterLab terminal via POST /api/terminals, connects via WebSocket, and executes arbitrary shell commands — achieving full RCE. An adversary can leverage this to exfiltrate secrets or credentials from the victim's environment.



Scope of impact

We discovered this issue during internal security testing. The issue is present in the default configuration of JupyterLab when the jupyterlab-git extension is installed.

The attack requires:

- The adversary to have commit access to a Git repository that the victim has cloned

- The victim to navigate to the Git History tab, click the rename commit, and click the renamed file to view the diff



The issue could allow an actor who has access to a shared Git repository to execute arbitrary JavaScript in another user's JupyterLab environment by committing a file with a crafted filename, potentially leading to remote code execution with access to user code, data, environment variables, and credentials.



Proof of concept

The issue exists in the createHeader() method where filenames from rename history are passed directly to innerHTML without sanitization:

[1] https://github.com/jupyterlab/jupyterlab-git/blob/main/src/components/diff/PlainTextDiff.ts#L214



Attack flow:

1. An adversary creates a file with a crafted filename containing a JavaScript payload, e.g., <img src=x onerror=eval(atob("base64_payload"))>.py

2. The adversary renames the file in a subsequent commit and pushes both commits to a shared Git repository

3. The victim clones or pulls the repository and navigates to the Git History tab in JupyterLab

4. The victim clicks the rename commit, then clicks the renamed file to view the diff

5. The createHeader() method constructs a diff header using string concatenation with the unsanitized filename and assigns the result to innerHTML

6. The injected JavaScript executes in the victim's browser session, reads the _xsrf cookie, sends a POST request to /api/terminals to open a JupyterLab terminal, connects via WebSocket, and executes arbitrary shell commands



Proof-of-concept mitigation

The issue can be mitigated by replacing innerHTML with textContent for filename rendering in the createHeader() method of PlainTextDiff.ts. Alternatively, proper HTML sanitization (escaping <, >, &, ", ') can be applied before inserting user-controlled filenames into the DOM.

## References
- https://github.com/jupyterlab/jupyterlab-git/security/advisories/GHSA-f962-v9hr-pfg5
- https://github.com/jupyterlab/jupyterlab-git
