# [H] PraisonAI: IMAP Command Injection via Unsanitized Email Search Parameters

## Summary
Severity: High
Advisory: GHSA-c969-5x3p-vq3v
CVE: CVE-2026-57130
CWE: CWE-20, CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-c969-5x3p-vq3v
Type: github-advisory

## Affected
- PyPI: `praisonaiagents` — affected >=0 <1.6.59

## Details
## Summary

The email search tool in `src/praisonai-agents/praisonaiagents/tools/email_tools.py` constructs IMAP SEARCH commands by interpolating LLM-controlled parameters (from_addr, subject, query) directly into IMAP protocol strings using f-string formatting with double-quote delimiters. An attacker who can influence the arguments to the `search_emails` or `reply_email` tool (via crafted agent prompts) can inject arbitrary IMAP commands, potentially exfiltrating email data from other folders, deleting emails, or performing other unauthorized IMAP operations.
## Details

**Vulnerable code (lines 493–502):**
```python
criteria = []
if from_addr:
    criteria.append(f'FROM "{from_addr}"')
if subject:
    criteria.append(f'SUBJECT "{subject}"')
if query:
    criteria.append(f'TEXT "{query}"')
if not criteria:
    criteria.append("ALL")
search_str = " ".join(criteria)
status, data = mail.search(None, search_str)
```

The `from_addr`, `subject`, and `query` parameters originate from LLM tool call arguments (the `search_emails` public function at line 665). These values flow through without any sanitization or escaping. The double-quote (`"`) characters in these parameters allow breaking out of the IMAP SEARCH quoted string context.

**Additional injection points:**
- Line 416: `mail.search(None, f'HEADER Message-ID "{search_id}"')`
- Line 447: Same pattern in `_smtp_reply_email`
- Line 542: Same pattern in `_smtp_archive_email`

The `search_id` / `message_id` parameter in these functions is also LLM-controlled via the `reply_email` and `archive_email` public tool functions.

**Reachability:** The `search_emails`, `reply_email`, and `archive_email` functions are exposed as agent tools. They are reachable when an agent is configured with email tools (EMAIL_ADDRESS + EMAIL_PASSWORD environment variables set). This is a documented deployment scenario for email-capable agents.

## PoC

**Setup:** Requires an IMAP server (not run here — this is a static proof). The vulnerability is demonstrated by tracing the data flow.

**Positive trigger — IMAP injection via `search_emails`:**
An LLM agent processing a crafted prompt calls:
```python
search_emails(from_addr='user@example.com" LOGOUT')
```
This produces the IMAP command:
```
SEARCH FROM "user@example.com" LOGOUT"
```
The `LOGOUT` command is injected after the prematurely closed quoted string, causing the IMAP connection to be terminated.

**More severe injection — exfiltrate emails from another folder:**
```python
search_emails(query='" SEARCH RETURN (MIN) ALL')
```
Produces: `TEXT "" SEARCH RETURN (MIN) ALL"` — injects a secondary SEARCH command.

**Negative control — legitimate search:**
```python
search_emails(from_addr='user@example.com')
```
Produces: `FROM "user@example.com"` — correct, no injection.

**Cleanup:** No persistent changes for read-only injection. For destructive injection (DELETE, EXPUNGE), impact persists.

## Impact

An attacker who can craft prompts that cause an LLM agent to call `search_emails` with injection payloads can:

- **Terminate IMAP connections** (denial of service)
- **Inject arbitrary IMAP commands** — including LIST (enumerate folders), SELECT (switch folders), FETCH (read emails from other mailboxes), STORE (modify flags), COPY/MOVE (move emails), DELETE/EXPUNGE (permanently delete emails)
- **Exfiltrate email contents** from folders the user did not intend to expose to the agent
- **Permanently delete emails** via injected DELETE + EXPUNGE commands

The attack requires the IMAP backend to be configured (EMAIL_ADDRESS + EMAIL_PASSWORD env vars), which is a documented and common deployment for email-capable agents.

## Suggested remediation

1. **Escape double-quote characters** in IMAP parameters. Per RFC 3501, literal strings use `{n}\r\n` format or quoted strings with `\` escaping:
```python
def _escape_imap_string(s: str) -> str:
    """Escape a string for safe use in IMAP quoted strings."""
    # Use IMAP literal syntax for safety: {length}\r\n<data>
    encoded = s.encode('utf-8')
    return f'{{{len(encoded)}}}\r\n{encoded}'
```

2. Use IMAP literal syntax (`{n}\r\ndata`) instead of quoted strings for all user-controlled parameters. This prevents any injection regardless of content.

3. Apply the escaping to all IMAP search criteria parameters: `from_addr`, `subject`, `query`, and `search_id`/`message_id`.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-c969-5x3p-vq3v
- https://github.com/MervinPraison/PraisonAI
