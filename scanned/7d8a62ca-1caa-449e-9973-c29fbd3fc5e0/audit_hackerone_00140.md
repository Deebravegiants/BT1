# [H] Improper handling of untypical characters in domain names

## Summary
Severity: High (CVSS 7.5)
Program: Node.js
Weakness: Improper Null Termination
Reporter: philippjeitner
State: resolved
Disclosed: 2021-09-10T17:51:58.124Z
CVE: CVE-2021-22931
Source: https://hackerone.com/reports/1178337

## Details
# Description

Missing input validation of host names returned by Domain Name Servers in node's `dns` library can lead to output of wrong hostnames (leading to Domain Hijacking) and injection vulnerabilities in applications using the library (leading to Remote Code Execution, XSS, Applications crashes, etc.).

# Discoverer(s)/Credits

Philipp Jeitner, Fraunhofer SIT

# References

Injection Attacks Reloaded: Tunnelling Malicious Payloads over DNS
https://www.usenix.org/conference/usenixsecurity21/presentation/jeitner
(Available starting from August 11, 2021)

# Steps To Reproduce

Using the example application (`main.js`) which does dns lookups via node.

```
const dns = require('dns');

if (process.argv[2] == "-x") {
	var host = process.argv[3];

	dns.reverse(host, (err, result) => {
		
		if (result){
			for (var i = 0; i < result.length; i++)
			{
				console.log("node".padEnd(8), "reverse".padEnd(16), host.padEnd(30), "-".padEnd(80), "-".padEnd(10), "IN".padEnd(5), "PTR".padEnd(5), result[i]);
			}
		} else {
			console.log("node".padEnd(8), "reverse".padEnd(16), host.padEnd(30), "-".padEnd(80), "-".padEnd(10), "-".padEnd(5), "ERROR".padEnd(5), err.errno);
		}
	});
	
} else {
	var host = process.argv[2];
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1178337_
