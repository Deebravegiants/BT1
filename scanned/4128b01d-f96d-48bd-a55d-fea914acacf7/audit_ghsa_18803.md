# [M] FastMCP vulnerable to reflected XSS in client's callback page

## Summary
Severity: Medium
Advisory: GHSA-mxxr-jv3v-6pgc
CVE: CVE-2025-62800
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-mxxr-jv3v-6pgc
Type: github-advisory

## Affected
- PyPI: `fastmcp` — affected >=0 <2.13.0

## Details
### Summary
While setting up an oauth client, it was noticed that the callback page hosted by the client during the flow embeds user-controlled content without escaping or sanitizing it. This leads to a reflected Cross-Site-Scripting vulnerability.

### Details
The affected code is located in *https://github.com/jlowin/fastmcp/blob/main/src/fastmcp/client/oauth_callback.py*, which embeds all values passed to the `create_callback_html` function via the `message` parameter it into the callback page without escaping them. This can, for example, be abused by calling the callback server with an XSS payload inside the `error` GET parameter, the value of which will then be inserted into the callback page, causing the execution of attacker-controlled JavaScript code in the callback server's origin. Note that besides the `error` parameter, other parameters reaching this function are affected too.

### PoC
1. Setup a simple fastmcp client such as this one (the callback server's port was fixated for simplicity):

```
url="http://127.0.0.1:8000/mcp"
oauth = OAuth(mcp_url=url,callback_port=1337)

async def main():
    async with Client(url, auth=oauth) as client:
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()

        print(f"tools: {tools}")
       
asyncio.run(main())
```

2. Ensure that the MCP server located at `http://127.0.0.1:8000/mcp` supports oauth.
3. Start the client.
4. As soon as the callback server has been started, access `http://localhost:1337/callback?error=<img/src/onerror=alert(window.origin)>`

Note that the exploitation could also for example be initiated by a malicious authorization server by returning the exploitation URL mentioned before in the `authorization_endpoint` field. The client would then automatically open, causing the XSS to trigger immediatly.

### Impact
The impact of this XSS vulnerability is the arbitrary JavaScript execution in the victim's browser in the callback server's origin.

## References
- https://github.com/jlowin/fastmcp/security/advisories/GHSA-mxxr-jv3v-6pgc
- https://nvd.nist.gov/vuln/detail/CVE-2025-62800
- https://github.com/jlowin/fastmcp/pull/2090
- https://github.com/jlowin/fastmcp/commit/2a20f54617a37213ed83894a8c2f0ac38a2e83a3
- https://github.com/jlowin/fastmcp
