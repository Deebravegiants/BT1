# [C] Command Injection in adb-mcp MCP Server

## Summary
Severity: Critical
Advisory: GHSA-54j7-grvr-9xwg
CVE: CVE-2025-59834
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-24
Source: https://github.com/advisories/GHSA-54j7-grvr-9xwg
Type: github-advisory

## Affected
- npm: `adb-mcp` — affected >=0

## Details
# Command Injection in adb-mcp MCP Server

The MCP Server at https://github.com/srmorete/adb-mcp is written in a way that is vulnerable to command injection vulnerability attacks as part of some of its MCP Server tool definition and implementation.

The MCP Server is also published publicly to npm at www.npmjs.com/package/adb-mcp and allows users to install it.

## Vulnerable tool

The MCP Server defines the function `executeAdbCommand()` which executes commands via string as a parameter and wraps the promise-based `exec` function.

The MCP Server then exposes the tool `inspect_ui` which relies on Node.js child process API `exec` (through the function wrapper) to execute the Android debugging command (`adb`). Relying on `exec` is an unsafe and vulnerable API if concatenated with untrusted user input.

Data flows from the tool definition [here](https://github.com/srmorete/adb-mcp/blob/master/src/index.ts#L334-L343) which takes in `args.device` and calls `execPromise()` in [this definitino](https://github.com/srmorete/adb-mcp/blob/master/src/index.ts#L346-L348C13) that uses `exec` in an insecure way.

Vulnerable line of code: [https://github.com/srmorete/adb-mcp/blob/master/src/index.ts#L334-L352](https://github.com/srmorete/adb-mcp/blob/master/src/index.ts#L334-L355)

```js
// Add adb UI dump tool
server.tool(
  "inspect_ui",
  AdbUidumpSchema.shape,
  async (args: z.infer<typeof AdbUidumpSchema>, _extra: RequestHandlerExtra) => {
    log(LogLevel.INFO, "Dumping UI hierarchy");
    
    const deviceArg = formatDeviceArg(args.device);
    const tempFilePath = createTempFilePath("adb-mcp", "window_dump.xml");
    const remotePath = args.outputPath || "/sdcard/window_dump.xml";
    
    try {
      // Dump UI hierarchy on device
      const dumpCommand = `adb ${deviceArg}shell uiautomator dump ${remotePath}`;
      await execPromise(dumpCommand);
      
      // Pull the UI dump from the device
      const pullCommand = `adb ${deviceArg}pull ${remotePath} ${tempFilePath}`;
      await execPromise(pullCommand);
      
      // Clean up the remote file
      await execPromise(`adb ${deviceArg}shell rm ${remotePath}`);
```

The argument to the tool, `AdbDevicesSchema`, is a Zod inferred type defined in the `src/types.ts` file in the project:

```js
export const inspectUiInputSchema = {
  device: z.string().optional().describe("Specific device ID (optional)"),
  outputPath: z.string().optional().describe("Custom output path on device (default: /sdcard/window_dump.xml)"),
  asBase64: z.boolean().optional().default(false).describe("Return XML content as base64 (default: false)")
};
```

and exposes `device` as a string which is an open way to trick the LLM into pushing arbitrary strings into it and hence achieve the command injection exploitation.


## Exploitation

When LLMs are tricked through prompt injection (and other techniques and attack vectors) to call the tool with input that uses special shell characters such as `; rm -rf /tmp;#` (be careful actually executing this payload) and other payload variations, the full command-line text will be interepted by the shell and result in other commands except of `ps` executing on the host running the MCP Server.

Reference example from prior security research on this topic, demonstrating how a similarly vulnerable MCP Server connected to Cursor is abused with prompt injection to bypass the developer's intended command:

![Cursor defined MCP Server vulnerable to command injection](https://res.cloudinary.com/snyk/image/upload/f_auto,w_2560,q_auto/v1747081395/Screenshot_2025-05-07_at_9.22.11_AM_d76kvm.png)

## Impact

User initiated and remote command injection on a running MCP Server.

## Recommendation

- Don't use `exec`. Use `execFile` instead, which pins the command and provides the arguments as array elements.
- If the user input is not a command-line flag, use the `--` notation to terminate command and command-line flag, and indicate that the text after the `--` double dash notation is benign value.

## References and Prior work

1. Command Injection in codehooks-mcp-server MCP Server project https://www.nodejs-security.com/blog/command-injection-vulnerability-codehooks-mcp-server-security-analysis identified as CVE-2025-53100
2. Command Injection in ios-simulator-mcp-server MCP Server project https://www.nodejs-security.com/blog/ios-simulator-mcp-server-command-injection-vulnerability identified as CVE-2025-52573
3. Liran's [Node.js Secure Coding: Defending Against Command Injection Vulnerabilities](https://www.nodejs-security.com/book/command-injection)

## Credit

Disclosed by [Liran Tal](https://lirantal.com)

## References
- https://github.com/srmorete/adb-mcp/security/advisories/GHSA-54j7-grvr-9xwg
- https://nvd.nist.gov/vuln/detail/CVE-2025-59834
- https://github.com/srmorete/adb-mcp/commit/041729c0b25432df3199ff71b3163a307cf4c28c
- https://github.com/srmorete/adb-mcp
- https://github.com/srmorete/adb-mcp/blob/master/src/index.ts#L334-L355
