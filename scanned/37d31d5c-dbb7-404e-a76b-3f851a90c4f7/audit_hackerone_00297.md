# [H] mod_http2, memory corruption on early pushes (CVE-2019-10081)

## Summary
Severity: High (CVSS 8.6)
Program: Internet Bug Bounty
Weakness: Use After Free
Reporter: cy1337
State: resolved
Disclosed: 2019-10-15T18:00:26.476Z
CVE: CVE-2019-10081
Source: https://hackerone.com/reports/677557

## Details
HTTP/2 very early pushes, for example configured with `H2PushResource`, could lead to an overwrite of memory in the pushing request's pool, leading to crashes. The memory copied is that of the configured push link header values, not data supplied by the client. Scenarios where an attacker may be able to influence response header values could potentially lead to controlled code execution. (Code execution has not been demonstrated and is unlikely with the config included here.) This issue affects versions 2.4.20 through 2.4.39.

This CVE is noted on the [Apache HTTPD advisory list](https://httpd.apache.org/security/vulnerabilities_24.html) as of August 14, 2019.

Reproduction is possible under ASAN builds of HTTPD with `MaxMemFree 1` and `H2Push On`

The following supplement to the default configuration is used:
```
Protocols h2c http/1.1
MaxMemFree 1
H2Push On
H2EarlyHints On
H2MaxSessionStreams 65535
H2WindowSize 65535
H2MinWorkers 5
H2MaxWorkers 32
H2MaxWorkerIdleSeconds 3
H2StreamMaxMemSize 1024
H2SerializeHeaders on
H2CopyFiles on
H2Padding 7
<Location />
    Header add Link "</xxx.css>;rel=preload"
    Header add Link "</xxx.js>;rel=preload"
    H2PushResource /xxx2.css
    H2PushResource /xxx3.css
    H2PushResource /
</Location> 
```

Under this configuration, the UAF is easily observed when handling traffic from [http2fuzz](https://github.com/c0nrad/http2fuzz). The behavior is affected by the size of responses and frequency of requests.

ASAN reports for these crashes are interesting because the faulting address tends to be an ASCII string. 

Here is a report where it manifested as a SEGV on an address which is actually an ASCII string (`0x44415445 == "DATE"`):
```
=================================================================
==7224==ERROR: AddressSanitizer: SEGV on unknown address 0x000044415445 (pc 0x00000068a8a3 bp 0x7fd8cf572a30 sp 0x7fd8cf5728d0 T1021)
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/677557_
