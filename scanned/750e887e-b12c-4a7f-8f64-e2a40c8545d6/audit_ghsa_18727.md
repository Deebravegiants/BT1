# [H] Home Assistant has Stored XSS vulnerability in Energy dashboard from Energy Entity Name

## Summary
Severity: High
Advisory: GHSA-mq77-rv97-285m
CVE: CVE-2025-62172
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:A/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P (CVSS_V4)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-mq77-rv97-285m
Type: github-advisory

## Affected
- PyPI: `homeassistant` — affected >=2025.1.0 <2025.10.2

## Details
### Summary
An authenticated party can add a malicious name to the Energy entity, allowing for Cross-Site Scripting attacks against anyone who can see the Energy dashboard, when they hover over any information point (The blue bar in the picture below)
<img width="955" height="568" alt="1_cens" src="https://github.com/user-attachments/assets/ed855216-c306-4b50-affc-cda100e72b74" />


An alternative, and more impactful scenario, is that the entity gets a malicious name from the provider of the Entity (in this case the energy provider: Tibber), and gets exploited that way, through the default name.


### Details
The incriminating entity in my scenario is from the Tibber integration, as shown in the screenshot below:
<img width="822" height="309" alt="2_cens" src="https://github.com/user-attachments/assets/d0d5a7aa-8d0c-4dcb-825b-e4cb8ea8885b" />


The exploit should be possible regardless of the Energy integration, as the user can name the entity themselves and as such pick a malicious name. The default name given by the Energy integration can also be taken directly from their system, and be vulnerable that way. The execution happens within the energy dashboard, when hovering over a data point:

<img width="1545" height="571" alt="image" src="https://github.com/user-attachments/assets/46dc7f00-4593-4271-8c3f-4c02b021ff2b" />


**Update found after issue was reported:**
I found that the issue presents itself for any entity with a html-entity in the name, which is included and rendered in the graph view. Following is an example for a speaker:
<img width="423" height="96" alt="11_cens" src="https://github.com/user-attachments/assets/3b4d43dd-d9e0-466b-85c0-277af3195acf" />

##### Source code
The relevant source code is added in a comment, but copy pasted here as well:

The offending line of code rendering the payload appears to be:
https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/panels/lovelace/cards/energy/hui-energy-devices-graph-card.ts#L110
Where the parameter marked with bold and italic is the vulnerable value:
return \`${title}${params.marker} **_${params.seriesName}_**: ${value}\`;


From the trace below, we can see that the only change done to the friendly_name of an entity is replacing underscores with spaces (_computeObjectId(entityId).replace(/_/g, " ")_).
We can also determine that any power entity will have it's name used if there is one, and fall back to the friendly name if it cannot find one:
```
data.push({
  id: `${compare ? "compare-" : ""}${statId}-${type}`,
  type: "bar",
  cursor: "default",
  name:
    type in labels
      ? labels[type]
      : getStatisticLabel(
          this.hass,
          statId,
          statisticsMetaData[statId]
        ),
```
(https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/panels/lovelace/cards/energy/hui-energy-usage-graph-card.ts#L467-L478)


The value comes from:

1. https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/panels/lovelace/cards/energy/hui-energy-usage-graph-card.ts#L467-L478 
(This is the relevant call: _getStatisticLabel(this.hass, statId, statisticsMetaData[statId];_)

2. getStatisticLabel is defined here: https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/data/recorder.ts#L329-L339 (This is the relevant call: _computeStateName(entity);_)

3. computeStateName is defined here: https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/common/entity/compute_state_name.ts


-----

### PoC
1. Set up a new energy provider with a price sensor.
2. Give the price sensor a malicious name 
<img width="814" height="100" alt="4_cens" src="https://github.com/user-attachments/assets/64bf7a00-47a2-46db-ae0f-b93e328837d2" />
<img width="459" height="325" alt="5_cens" src="https://github.com/user-attachments/assets/e43e1c4f-bb4e-45b4-b46a-a6fc32b689ba" />


3. Configure the energy dashboard to get data from the price sensor
<img width="582" height="394" alt="image" src="https://github.com/user-attachments/assets/74c99ab8-0842-4c1b-b2e9-994827d89609" />

<img width="1678" height="241" alt="7_cens" src="https://github.com/user-attachments/assets/24f4c83a-3c0a-4dea-9e1c-9c6b070fb28f" />


<img width="329" height="497" alt="8_cens" src="https://github.com/user-attachments/assets/ccb7f90a-4745-4fb4-9efa-f30b3324cb3a" />


5. Look at the data and hover the data point for code to execute. (You may have to trigger data ingestion or add a false data point to be able to hover a data point when testing, you need at least one datapoint to trigger the vulnerability)
<img width="1547" height="575" alt="9_cens" src="https://github.com/user-attachments/assets/087cdf78-a503-427d-8e0c-bb5db24de5c8" />


### Impact
It is possible to exploit this over the internet, by using an energy provider, like Tibber, with a malicious name, and relying on the default naming in Home Assistant being used. This is actually how I found this bug:
<img width="453" height="152" alt="10_cens" src="https://github.com/user-attachments/assets/45451efb-2688-4589-a988-88d1fc0b4e25" />

This means that a malicious employee or someone with access to your electricity provider can attack your Home Assistant instance from your electricity provider. I am unsure if you consider this a sanitization and escaping issue in the respective integrations or not, but I believe a central fix in the form of fixing the Energy Dashboard is more appropriate, rather than to rely on every integration properly handling user input.

## References
- https://github.com/home-assistant/core/security/advisories/GHSA-mq77-rv97-285m
- https://nvd.nist.gov/vuln/detail/CVE-2025-62172
- https://github.com/home-assistant/core
- https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/common/entity/compute_state_name.ts
- https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/data/recorder.ts#L329-L339
- https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/panels/lovelace/cards/energy/hui-energy-devices-graph-card.ts#L110
- https://github.com/home-assistant/frontend/blob/c13a80ce5e7ae39f0262444e2b6295a074a96732/src/panels/lovelace/cards/energy/hui-energy-usage-graph-card.ts#L467-L478
