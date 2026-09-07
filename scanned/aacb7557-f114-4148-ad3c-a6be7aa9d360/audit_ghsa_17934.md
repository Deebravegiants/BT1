# [M] Mermaid improperly sanitizes sequence diagram labels leading to XSS

## Summary
Severity: Medium
Advisory: GHSA-7rqq-prvp-x9jh
CVE: CVE-2025-54881
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-7rqq-prvp-x9jh
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=11.0.0-alpha.1 <11.10.0
- npm: `mermaid` — affected >=10.9.0-rc.1 <10.9.4

## Details
### Summary
In the default configuration of mermaid 11.9.0, user supplied input for sequence diagram labels is passed to `innerHTML` during calculation of element size, causing XSS.

### Details
Sequence diagram node labels with KaTeX delimiters are passed through `calculateMathMLDimensions`. This method passes the full label to `innerHTML` which allows allows malicious users to inject arbitrary HTML and cause XSS when mermaid-js is used in it's default configuration (with KaTeX support enabled). 

The vulnerability lies here:

```ts
export const calculateMathMLDimensions = async (text: string, config: MermaidConfig) => {
  text = await renderKatex(text, config);
  const divElem = document.createElement('div');
  divElem.innerHTML = text; // XSS sink, text has not been sanitized.
  divElem.id = 'katex-temp';
  divElem.style.visibility = 'hidden';
  divElem.style.position = 'absolute';
  divElem.style.top = '0';
  const body = document.querySelector('body');
  body?.insertAdjacentElement('beforeend', divElem);
  const dim = { width: divElem.clientWidth, height: divElem.clientHeight };
  divElem.remove();
  return dim;
};
```

The `calculateMathMLDimensions` method was introduced in 5c69e5fdb004a6d0a2abe97e23d26e223a059832 two years ago, which was released in [Mermaid 10.9.0](https://github.com/mermaid-js/mermaid/releases/tag/v10.9.0).

### PoC
Render the following diagram and observe the modified DOM.

```
sequenceDiagram
    participant A as Alice<img src="x" onerror="document.write(`xss on ${document.domain}`)">$$\\text{Alice}$$
    A->>John: Hello John, how are you?
    Alice-)John: See you later!
```

Here is a PoC on mermaid.live: https://mermaid.live/edit#pako:eNpVUMtOwzAQ_BWzyoFKaRTyaFILiio4IK7ckA-1km1iKbaLY6spUf4dJ0AF68uOZ2dm7REqXSNQ6PHDoarwWfDGcMkUudaJGysqceLKkj3hPdl3osJ7IRvSm-qBwcCAaIXGaONRrSsnUdnobITF28PQ954lwXglai25UNNhxWAXBMyXxcGOi-3kL_5k79e73atuFSUv2HWazH1IWn0m3CC5aPf4b3p2WK--BW-4DJCOWzQ3TM0HQmiMqIFa4zAEicZv4iGMsw0D26JEBtS3NR656ywDpiYv869_11r-Ko12TQv0yLveI3eqfcjP111HUNVonrRTFuhdsVgAHWEAmuRxlG7SuEzKMi-yJAnhAjTLIk_EcbFJtuk2y9MphM8lM47KIp--AOZghtU

### Impact
XSS on all sites that use mermaid and render user supplied diagrams without further sanitization.

### Remediation
The value of the `text` argument for the `calculateMathMLDimensions` method needs to be sanitized before getting passed on to `innerHTML`.

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-7rqq-prvp-x9jh
- https://nvd.nist.gov/vuln/detail/CVE-2025-54881
- https://github.com/mermaid-js/mermaid/commit/5c69e5fdb004a6d0a2abe97e23d26e223a059832
- https://github.com/mermaid-js/mermaid/commit/685516a85ec1df64cefd4fd15f26533be87d458e
- https://github.com/mermaid-js/mermaid
