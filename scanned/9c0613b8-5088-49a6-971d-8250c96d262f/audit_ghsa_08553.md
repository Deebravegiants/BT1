# [H] Open WebUI's chat completion API allows tool restrictions to be bypassed

## Summary
Severity: High
Advisory: GHSA-4pcg-253r-rf9w
CVE: CVE-2026-45350
CWE: CWE-862
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-4pcg-253r-rf9w
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.8.6

## Details
### Summary
Open WebUI v0.6.43 contains a vulnerability in its chat completion API, which allows attackers to bypass tool restrictions, potentially enabling unauthorized actions or access.


### Details
In the [chat_completion](https://github.com/open-webui/open-webui/blob/a7271532f8a38da46785afcaa7e65f9a45e7d753/backend/open_webui/main.py#L1529) API, the parameters [tool_ids and tool_servers](https://github.com/open-webui/open-webui/blob/a7271532f8a38da46785afcaa7e65f9a45e7d753/backend/open_webui/main.py#L1613-L1614) are supplied by the user. These parameters are used to [create a tools_dict by the middleware](https://github.com/open-webui/open-webui/blob/a7271532f8a38da46785afcaa7e65f9a45e7d753/backend/open_webui/utils/middleware.py#L1394). This is then used by [get_tool_by_id](https://github.com/open-webui/open-webui/blob/a7271532f8a38da46785afcaa7e65f9a45e7d753/backend/open_webui/models/tools.py#L139) to retrieve the appropriate tool. However, there is no checks in that ensures the user that uses the API has permission to use the tool, meaning that a user can invoke any server tool by supplying the correct tool_id or tool_servers parameters via the chat completion API. Moreover, the authentication token stored in the server would be used when invoking the tool, so the tool will be invoked with the server privilege.
### PoC
To reproduce the issue, create an admin user and create an external tool via the admin settings. Set the type to "MCP Streamable HTTP" for the tool, and the url pointing to a mcp server. For example, the public instance of the ["Fetch" mcp server](https://github.com/modelcontextprotocol/servers/blob/main/src/fetch/README.md) can be used, which is located at "https://remote.mcpservers.org/fetch/mcp". Other mcp servers, e.g. the GitHub MCP server can also be used. Then set the "Auth" field appropriately. (Fetch mcp does not require Auth to be set).

Set the ID, name and description for the MCP server and set visibility to private. This should prevent any user from using the mcp server. (For the example below, we use the fetch mcp server and set the ID to 1)

Next create a user with low privilege and enable API keys from the admin settings.

Then use the chat completion API with the low privilege user with a prompt specifying the use of the restricted tool, and include the id of the tool in the tool_ids parameter. For example, to use the fetch mcp server set up before:

```
def chat_with_model(token):
    url = 'http://localhost:3000/api/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
      "model": "llama3.1:latest",
      "messages": [
        {
          "role": "user",
          "content": "Use the fetch tool to fetch content of the url https://raw.githubusercontent.com/modelcontextprotocol/servers/refs/heads/main/src/fetch/LICENSE"
        }],
        
        "tool_ids" : [
            "server:mcp:1",
        ],
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()
```

Note that the tool will be used to fetch the content of the file, despite the tool is restricted and has it's visibility set to private

### Impact
This issue may lead to restricted tools being invoked by users via the chat completion API

## Resolution

Fixed across two releases

- **Local Tool records** (`tool_ids: ["<tool_id>"]` referencing a stored Tool): fixed in commit [9b06fdc8f](https://github.com/open-webui/open-webui/commit/9b06fdc8fe1c933071610336be05f11e77e6c8eb), first released in **v0.7.0**. `get_tools()` in `backend/open_webui/utils/tools.py` (line 166) now resolves the caller's group memberships and rejects each requested `tool_id` whose owner isn't the caller and for which no `AccessGrants.has_access(resource_type='tool', permission='read')` grant exists. Admins continue to bypass when `BYPASS_ADMIN_ACCESS_CONTROL` is enabled (its documented UI/posture purpose).

- **Admin-configured MCP servers** (`tool_ids: ["server:mcp:<id>"]`, the report's exact PoC): fixed in commit [4737e1f11](https://github.com/open-webui/open-webui/commit/4737e1f11), first released in **v0.8.6**. The MCP-resolution loop in `backend/open_webui/utils/middleware.py` (line 2670) now calls `has_connection_access(user, mcp_server_connection)` and skips the server with a warning if the user has no grant — the server's stored credentials are never used on behalf of an unauthorized caller.

Users on `>= 0.8.6` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-4pcg-253r-rf9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-45350
- https://github.com/open-webui/open-webui/commit/4737e1f11
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.8.6
