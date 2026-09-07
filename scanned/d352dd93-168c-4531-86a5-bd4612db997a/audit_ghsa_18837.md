# [M] python-socketio vulnerable to arbitrary Python code execution (RCE) through malicious pickle deserialization in certain multi-server deployments

## Summary
Severity: Medium
Advisory: GHSA-g8c6-8fjj-2r4m
CVE: CVE-2025-61765
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-g8c6-8fjj-2r4m
Type: github-advisory

## Affected
- PyPI: `python-socketio` — affected >=0.8.0 <5.14.0

## Details
### Summary
A remote code execution vulnerability in python-socketio versions prior to 5.14.0 allows attackers to execute arbitrary Python code through malicious pickle deserialization in multi-server deployments on which the attacker previously gained access to the message queue that the servers use for internal communications.

### Details
When Socket.IO servers are configured to use a message queue backend such as Redis for inter-server communication, messages sent between the servers are encoded using the `pickle` Python module. When a server receives one of these messages through the message queue, it assumes it is trusted and immediately deserializes it.

The vulnerability stems from deserialization of messages using Python's `pickle.loads()` function. Having previously obtained access to the message queue, the attacker can send a python-socketio server a crafted pickle payload that executes arbitrary code during deserialization via Python's `__reduce__` method.

### Impact
This vulnerability only affects deployments with a compromised message queue. The attack can lead to the attacker executing random code in the context of, and with the privileges of a Socket.IO server process. 

Single-server systems that do not use a message queue, and multi-server systems with a secure message queue are not vulnerable.

### Remediation
In addition to making sure standard security practices are followed in the deployment of the message queue, users of the python-socketio package can upgrade to version 5.14.0 or newer, which remove the `pickle` module and use the much safer JSON encoding for inter-server messaging.

## References
- https://github.com/miguelgrinberg/python-socketio/security/advisories/GHSA-g8c6-8fjj-2r4m
- https://nvd.nist.gov/vuln/detail/CVE-2025-61765
- https://github.com/miguelgrinberg/python-socketio/commit/53f6be094257ed81476b0e212c8cddd6d06ca39a
- https://github.com/miguelgrinberg/python-socketio
- https://www.bluerock.io/post/cve-2025-61765-bluerock-discovers-critical-rce-in-socket-io-ecosystem
