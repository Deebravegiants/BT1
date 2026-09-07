# [M] Mermaid does not properly sanitize architecture diagram iconText leading to XSS

## Summary
Severity: Medium
Advisory: GHSA-8gwm-58g9-j8pw
CVE: CVE-2025-54880
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-8gwm-58g9-j8pw
Type: github-advisory

## Affected
- npm: `mermaid` — affected >=11.1.0 <11.10.0

## Details
### Summary
In the default configuration of mermaid 11.9.0, user supplied input for architecture diagram icons is passed to the d3 `html()` method, creating a sink for cross site scripting.

### Details
Architecture diagram service `iconText` values are passed to the d3 `html()` method, allowing malicious users to inject arbitrary HTML and cause XSS when mermaid-js is used in it's default configuration. 

The vulnerability lies here:

```ts
export const drawServices = async function (
  db: ArchitectureDB,
  elem: D3Element,
  services: ArchitectureService[]
): Promise<number> {
  for (const service of services) {
    /** ... **/
    } else if (service.iconText) {
      bkgElem.html(
        `<g>${await getIconSVG('blank', { height: iconSize, width: iconSize, fallbackPrefix: architectureIcons.prefix })}</g>`
      );
      const textElemContainer = bkgElem.append('g');
      const fo = textElemContainer
        .append('foreignObject')
        .attr('width', iconSize)
        .attr('height', iconSize);
      const divElem = fo
        .append('div')
        .attr('class', 'node-icon-text')
        .attr('style', `height: ${iconSize}px;`)
        .append('div')
        .html(service.iconText); // <- iconText passed into innerHTML
       /** ... **/
};
};
```

This issue was introduced with 734bde38777c9190a5a72e96421c83424442d4e4, around 15 months ago, which was released in [v11.1.0](https://github.com/mermaid-js/mermaid/releases/tag/mermaid%4011.1.0).

### PoC
Render the following diagram and observe the modified DOM.

```
architecture-beta
    group api(cloud)[API]
    service db "<img src=x onerror=\"document.write(`xss on ${document.domain}`)\">" [Database] in api
```

Here is a PoC on mermaid.live: https://mermaid.live/edit#pako:eNo9T8FOwzAM_ZXI4rBJpWrpRtuIISF24caZZdKyxOsiLUnlJjCo-u9kQ8wX-_n5-dkjKK8ROEhSRxNQhUh4v8cghWMpOvKxZ7I3M3XyUc83L-9v2z9qQPo0CpneMwFPxnZsILU6M--QyNNKCAHaq2jRhfyL0vLZ7jwMiWd3443Q3krjpt38Mv4sgG3WMsi9HHDLjLs4CwcZdGQ08EARM7BISZMgjJdLBIQjWhTAU6nxIOMpCBBuSrJeug_v7b8yPdMdgR_kaUgo9loGXBvZkbS3LqHTSK8-ugC8LMrrEuAjnIEvlnlVL9q6rZu6Lh-rRQbfwKuyyZuybcvqIaWiqKcMfq6uRd7Uy-kXhYFzcA

### Impact
XSS on all sites that use mermaid and render user supplied diagrams without further sanitization.

### Remediation
Sanitize the value of `iconText` before passing it to `html()`.

## References
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-8gwm-58g9-j8pw
- https://nvd.nist.gov/vuln/detail/CVE-2025-54880
- https://github.com/mermaid-js/mermaid/commit/2aa83302795183ea5c65caec3da1edd6cb4791fc
- https://github.com/mermaid-js/mermaid/commit/734bde38777c9190a5a72e96421c83424442d4e4
- https://github.com/mermaid-js/mermaid
