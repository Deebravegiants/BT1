# [C] OpenC3 COSMOS: Permissions Bypass Provides User Access to Unassigned Administrative Actions via Script Runner Tool

## Summary
Severity: Critical
Advisory: GHSA-2wvh-87g2-89hr
CWE: CWE-250
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-2wvh-87g2-89hr
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=0 <7.0.0-rc3

## Details
**Vulnerability Type: Execution with Unnecessary Privileges
Attack type: Authenticated remote
Impact: Data disclosure/manipulation, privilege escalation
Affected components: The following docker images:
•	Openc3inc/openc3-COSMOS-script-runner-api**

The Script Runner widget allows users to execute Python and Ruby scripts directly from the openc3-COSMOS-script-runner-api container. Because all the docker containers share a network, users can execute specially crafted scripts to bypass the API permissions check and perform administrative actions, including reading and modifying data inside the Redis database, which can be used to read secrets and change COSMOS settings, as well as read and write to the buckets service, which holds configuration, log, and plugin files. These actions are normally only available from the Admin Console or with administrative privileges. Any user with permission to create and run scripts can connect to any service in the docker network. 
 
<img width="940" height="473" alt="image" src="https://github.com/user-attachments/assets/bf524163-127d-4349-999b-cefc53d4374d" />

Figure 1: Environment variables, including Redis credentials, found in the Script Runner container
A Ruby script is used to expose the Redis username, password, hostname, and port. These credentials might also be found from the source code or through a brute-force attack.
 
<img width="940" height="507" alt="image" src="https://github.com/user-attachments/assets/6d3ccad4-949d-4eeb-a5f8-3aca48bbe815" />

Figure 2: A Python script is used to add data to Redis and retrieve the new data
A Python script is then used to create a new entry in the Redis database called `openc3__settings_hacked` with a key of `store_url` and a value of `http://hacked.com`.
 
<img width="940" height="70" alt="image" src="https://github.com/user-attachments/assets/fcef13be-5416-4627-9c95-617a24674ee0" />

Figure 3: The new data found in the Redis database
The new entry was successfully added to the Redis database, as is confirmed by using `redis-cli`. 
The following example shows how an attacker might change the plugin store URL file that is stored in the config bucket.
 
<img width="940" height="640" alt="image" src="https://github.com/user-attachments/assets/681b4dd6-4b6e-4a91-8480-0c9fbff76ede" />

Figure 4: Uploading file to change the plugin store URL setting
 
<img width="940" height="189" alt="image" src="https://github.com/user-attachments/assets/630db0bb-217e-4205-be1d-e9891516b22f" />

Figure 5: The URL file was successfully changed
###	Steps To Reproduce
1.	Run the following Ruby code to find the Redis credentials:
```ruby
puts `env | grep redis`
```
3.	Add the following Python script with the credentials to create a new entry and read it
```python
import redis
import json
import time

r = redis.Redis(
    host = 'openc3-redis',
    port = 6379,
    username = 'openc3', 
    password = 'openc3password',  
    decode_responses=True
)

# Save a setting
setting_data = {
    'name': 'store_url',
    'data': 'http://hacked.com',
    'updated_at': time.time_ns()
}
r.hset('openc3__settings_hacked','store_url',json.dumps(setting_data))
print(r.hget('openc3__settings_hacked','store_url'))
```

###	Recommendations
•	Limit the permissions of the script runner API to prevent lower level users from performing administrative actions

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-2wvh-87g2-89hr
- https://github.com/OpenC3/cosmos
